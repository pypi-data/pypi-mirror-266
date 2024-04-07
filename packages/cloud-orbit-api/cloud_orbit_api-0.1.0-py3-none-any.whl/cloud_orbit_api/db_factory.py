import sqlite3
import os

SQL_DB_PATH_DIR = os.environ.get("SQLITE_DB_DIR", "")
SQL_DB_NAME = os.environ.get("SQLITE_DB_NAME", "test.db")

class SQLiteSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if SQLiteSingleton._instance is None:
            SQLiteSingleton._instance = SQLiteSingleton()
            SQLiteSingleton._instance.conn = sqlite3.connect(os.path.join(SQL_DB_PATH_DIR, SQL_DB_NAME), check_same_thread=False)
            print('Opened database successfully')
            SQLiteSingleton._instance.cursor = SQLiteSingleton._instance.conn.cursor()
            SQLiteSingleton.create_table()
            print('created table successfully')

        return SQLiteSingleton._instance
    
    @staticmethod
    def create_table():
        # Create the items table if it doesn't exist
        SQLiteSingleton._instance.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        SQLiteSingleton._instance.conn.commit()
