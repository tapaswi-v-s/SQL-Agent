from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langgraph.graph.message import AnyMessage

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    tables: str