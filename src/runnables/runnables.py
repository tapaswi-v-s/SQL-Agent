from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools.tools import *
from .prompts import *
from dotenv import load_dotenv
load_dotenv()

class TableSelectionAssistant:
    table_selection_prompt = ChatPromptTemplate.from_messages([
        ("system", table_selection_prompt_text),
        ("placeholder", '{messages}')
    ])

    table_selection_llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)\
        .bind_tools([get_schema])
    
    table_selection_runnable = table_selection_prompt | table_selection_llm

    def invoke(self, dict):
        return self.table_selection_runnable.invoke(dict)
    
class ExamineQueryAssistant:

    examine_query_prompt = ChatPromptTemplate.from_messages([
        ('system', examine_query_prompt_text), ('placeholder', '{messages}')
    ])
    examine_query_llm = ChatOpenAI(model='gpt-4o', temperature=0)\
        .bind_tools([execute_DQL_query, execute_DML_query], tool_choice='required')

    examine_query_runnable = examine_query_prompt | examine_query_llm

    def invoke(self, dict):
        return self.examine_query_runnable.invoke(dict)
    
class SQLQueryAssistant:
    
    sql_query_prompt = ChatPromptTemplate.from_messages([
        ('system', sql_query_prompt_text),
        ('placeholder', '{messages}')
    ])
    sql_query_llm = ChatOpenAI(model='gpt-4o', temperature=0)\
        .bind_tools([submit_query])

    sql_query_runnable = sql_query_prompt | sql_query_llm

    def invoke(self, dict):
        return self.sql_query_runnable.invoke(dict)