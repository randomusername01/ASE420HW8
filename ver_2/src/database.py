import sqlite3

class Database:
    _instance = None

    def __init__(self):
        if Database._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.conn = sqlite3.connect("time_management.db")
            Database._instance = self

    def create_database():
        conn = Database.get_instance().get_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                task TEXT NOT NULL,
                tag TEXT
            );
        ''')

    @staticmethod
    def get_instance():
        if Database._instance is None:
            Database()
        return Database._instance

    def get_connection(self):
        return self.conn