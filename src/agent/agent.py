from tools.tools import *
from graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from typing import Optional
import json
import uuid

class Agent:
    def __init__(self) -> None:
        self.graph = Graph().get_graph()
        self.thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    def generate_verification_message(self, message: AIMessage) -> None:
        """Generate "verification message" from message with tool calls."""
        serialized_tool_calls = json.dumps(message.tool_calls,indent=2)

        return AIMessage(
            content=(
                "I plan to invoke the following tools, do you approve?\n\n"
                "Type 'y' if you do, anything else to stop.\n\n"
                f"{serialized_tool_calls}"
            ),
            id=message.id,
        )

    def stream_app_catch_tool_calls(self, inputs):
        """Stream graph, catching tool calls."""
        tool_call_message = None
        for event in self.graph.stream(inputs, self.thread, stream_mode="values"):
            message = event["messages"][-1]
            if isinstance(message, AIMessage) and message.tool_calls \
                and message.tool_calls[0]['name'] == execute_DML_query.name:
                tool_call_message = message
            else:
                message.pretty_print()
        return tool_call_message
    
    def execute(self, initial_message: str):
        """Execute the graph and handle interruptions."""
        tool_call_message = self.stream_app_catch_tool_calls(
            {"messages": [HumanMessage(initial_message)]}
        )

        while tool_call_message:
            verification_message = self.generate_verification_message(tool_call_message)
            verification_message.pretty_print()
            input_message = HumanMessage(input("Enter your input: "))
            if input_message.content.lower().strip() == "exit":
                print("Exiting the graph execution....")
                break
            input_message.pretty_print()

            snapshot = self.graph.get_state(self.thread)
            snapshot.values["messages"] += [verification_message, input_message]

            if input_message.content.strip().lower() in ['y', 'yes', 'ok']:
                tool_call_message.id = str(uuid.uuid4())
                snapshot.values["messages"] += [tool_call_message]
                self.graph.update_state(self.thread, snapshot.values, as_node="examine_query_assistant")
            else:
                self.graph.update_state(self.thread, snapshot.values, as_node="get_schema")

            tool_call_message = self.stream_app_catch_tool_calls(None)
