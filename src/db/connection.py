import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

class SQLiteConnection:
    """Class to manage SQLite database connection."""

    _instance = None
    _connection = None

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super(SQLiteConnection, cls).__new__(cls)
            db_path = db_path or os.getenv('DB_PATH', 'database.sqlite')
            try:
                cls._connection = sqlite3.connect(db_path, check_same_thread=False)
            except sqlite3.Error as e:
                cls._instance = None
                cls._connection = None
                raise e 
        return cls._instance

    def get_connection(self):
        if self._connection is None:
            raise sqlite3.Error("Database connection is not established.")
        return self._connection
    
    def get_cursor(self):
        if self._connection is None:
            raise sqlite3.Error("Database connection is not established.")
        return self._connection.cursor()
    
    def close(self):
        if self._connection:
            try:
                self._connection.close()
            except sqlite3.Error as e:
                raise e
            finally:
                SQLiteConnection._instance = None
                SQLiteConnection._connection = None