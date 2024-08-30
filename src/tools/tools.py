from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from db.connection import SQLiteConnection
import sqlite3


db = SQLiteConnection()
connection = db.get_connection()
cursor = db.get_cursor()
    
@tool
def get_tables() -> str:
    """A tool to fetch the names of the available tables in the database"""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = cursor.fetchall()
        names = ', '.join([row[0] for row in rows])
        return names
    except sqlite3.Error as e:
        return f"Error: {e}"

@tool
def get_schema(table_names: list[str]):
    """Tool to get the Schema(DDL) of the given table name"""
    try:
        ddls = []
        for table in table_names:
            cursor.execute(f"SELECT * FROM (SELECT * FROM sqlite_master WHERE type='table') \
                        WHERE name='{table}'")
            ddls.append(cursor.fetchone()[-1])
        return ddls
    except sqlite3.Error as e:
        return f"Error: {e}"

class QuerySchema(BaseModel):
    query: str = Field(description="should be a SQL query")

@tool("execute_DML_query", args_schema=QuerySchema, return_direct=True)
def execute_DML_query(query: str) -> str:
    """Tool to execute DML SQL queries like INSERT, UPDATE, DELETE queries that updates the database records"""
    try:
        cursor.execute(query)
        connection.commit()
        return "Operation Success"
    except sqlite3.Error as e:
        return f"Error: {e}"

@tool("execute_DQL_query", args_schema=QuerySchema, return_direct=True)
def execute_DQL_query(query: str):
    """Tool to execute DQL SQL queries like SELECT query that only reads data from the database"""
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        return f"Error: {e}"

@tool('submit_query', args_schema=QuerySchema, return_direct=True)
def submit_query(query: str):
    """A tool to submit the SQL query."""
    return query