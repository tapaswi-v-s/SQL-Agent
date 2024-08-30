from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, ToolMessage
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from .state import State
from runnables.runnables import *
from utils.utils import *


class Graph:
    workflow = StateGraph(State)

        ###### Nodes ######
    def table_selection_assistant(self, state: State):
        result = TableSelectionAssistant().invoke(state)
        return {'messages': result}

    def SQL_query_assistant(self, state: State):
        result = SQLQueryAssistant().invoke(state)
        return {'messages': [result]}

    def examine_query_assistant(self, state: State):
        # Adding Tool Message
        tool_call = state['messages'][-1].tool_calls[0]
        tool_message = ToolMessage(
            tool_call_id=tool_call['id'],
            name=tool_call['name'],
            content=submit_query.invoke(tool_call['args']))
        state['messages'] += [tool_message]

        result = ExamineQueryAssistant().invoke(state)
        return {'messages': result}
    
    ###### Routes ######
    def route_table_selection(self, state: State) -> Literal['get_schema', END]:
        route = tools_condition(state)
        if route == END:
            return END
        else:
            return 'get_schema'

    def route_query_check(self, state: State) -> Literal[
        'execute_DQL_query', 'execute_DML_query']:
        
        route = tools_condition(state)
        if route == END:
            return END
        
        tool_calls = state['messages'][-1].tool_calls

        if tool_calls[0]['name'] == execute_DQL_query.name:
            return execute_DQL_query.name
        else:
            return execute_DML_query.name
        
    def route_generate_query(self, state: State) -> Literal['examine_query_assistant', END]:
        route = tools_condition(state)
        if route == END:
            return END
        else:
            return 'examine_query_assistant'
        
    def __init__(self):
        ####### Defining Edges #######
        self.workflow.add_node('get_db_tables', lambda _ : {'tables': get_tables.invoke({})})
        self.workflow.add_node('table_selection_assistant', self.table_selection_assistant)
        self.workflow.add_node('get_schema', create_tool_node_with_fallback([get_schema]))
        self.workflow.add_node('SQL_query_assistant', self.SQL_query_assistant)
        self.workflow.add_node('examine_query_assistant', self.examine_query_assistant)

        self.workflow.add_node('execute_DQL_query', 
                        create_tool_node_with_fallback([execute_DQL_query]))
        self.workflow.add_node('execute_DML_query', ToolNode(tools=[execute_DML_query]))


        ####### Defining Edges #######
        self.workflow.add_edge(START, 'get_db_tables')
        self.workflow.add_edge('get_db_tables', 'table_selection_assistant')
        self.workflow.add_conditional_edges('table_selection_assistant', self.route_table_selection)
        self.workflow.add_edge('get_schema', 'SQL_query_assistant')
        self.workflow.add_conditional_edges('SQL_query_assistant', self.route_generate_query)
        self.workflow.add_conditional_edges('examine_query_assistant', self.route_query_check)
        self.workflow.add_edge('execute_DQL_query', 'SQL_query_assistant')
        self.workflow.add_edge('execute_DML_query', 'SQL_query_assistant')

        self.memory = MemorySaver()

        self.graph = self.workflow.compile(
            checkpointer=self.memory,
            interrupt_before=['execute_DML_query']
        )
    
    def get_graph(self):
        return self.graph