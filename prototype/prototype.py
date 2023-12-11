import sqlite3
from datetime import datetime


def create_database(database_name):
    conn = sqlite3.connect(database_name)
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
    conn.close()


def add_record(date, start_time, end_time, task, tag):
    try:
        conn = sqlite3.connect('../time_management.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (date, start_time, end_time, task, tag) VALUES (?, ?, ?, ?, ?)",
                       (date, start_time, end_time, task, tag))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def query_records(query):
    try:
        conn = sqlite3.connect('../time_management.db')
        cursor = conn.cursor()

        if query.lower() == 'today':
            query = datetime.today().strftime('%Y-%m-%d')

        # Case-insensitive query for task and tag
        cursor.execute("SELECT * FROM records WHERE date = ? OR LOWER(task) LIKE ? OR LOWER(tag) LIKE ?",
                       (query, '%' + query.lower() + '%', '%' + query.lower() + '%'))
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def parse_date(date_str):
    # Parses date string to the format 'YYYY-MM-DD'
    if date_str.lower() == 'today':
        return datetime.today().strftime('%Y-%m-%d')
    return date_str  # Add more logic if needed for other date formats


def main():
    create_database("time_management")
    while True:
        command = input("Enter your command: ")
        if command.lower().startswith('record'):
            parts = command.split(maxsplit=5)
            if len(parts) == 6:
                _, date_str, start_time, end_time, task, tag = parts
                date = parse_date(date_str)
                add_record(date, start_time, end_time, task.strip('‘’'), tag)
                print("Record added successfully.")
            else:
                print("Invalid record format. Please use 'record DATE FROM TO TASK TAG'.")
        elif command.lower().startswith('query'):
            _, query = command.split(maxsplit=1)
            records = query_records(query)
            for record in records:
                print(record)
        else:
            print("Invalid action. Please start with 'record' or 'query'.")


if __name__ == "__main__":
    main()
