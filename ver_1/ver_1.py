import sqlite3
from datetime import datetime

time_format_24hr = True


def create_database():
    conn = sqlite3.connect("time_management.db")
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
        conn = sqlite3.connect('time_management.db')
        cursor = conn.cursor()
        # Ensure start and end times are in 24-hour format
        start_time_24hr = convert_to_24hr_format(start_time)
        end_time_24hr = convert_to_24hr_format(end_time)
        cursor.execute("INSERT INTO records (date, start_time, end_time, task, tag) VALUES (?, ?, ?, ?, ?)",
                       (date, start_time_24hr, end_time_24hr, task, tag))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()



def query_records(query):
    try:
        conn = sqlite3.connect('time_management.db')
        cursor = conn.cursor()

        if query.lower() == 'today':
            query = datetime.today().strftime('%Y-%m-%d')

        cursor.execute("SELECT * FROM records WHERE date = ? OR LOWER(task) LIKE ? OR LOWER(tag) LIKE ?",
                       (query, '%' + query.lower() + '%', '%' + query.lower() + '%'))
        records = cursor.fetchall()

        formatted_records = []
        for record in records:
            id, date, start_time, end_time, task, tag = record
            start_time = format_time_for_display(start_time)
            end_time = format_time_for_display(end_time)
            formatted_records.append((id, date, start_time, end_time, task, tag))

        return formatted_records
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def parse_date(date_str):
    # Parses date string to the format 'YYYY-MM-DD'
    if date_str.lower() == 'today':
        return datetime.today().strftime('%Y-%m-%d')
    return date_str  # Add more logic if needed for other date formats


def generate_report(start_date, end_date):
    try:
        conn = sqlite3.connect('time_management.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM records WHERE date BETWEEN ? AND ?", (start_date, end_date))
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def get_activity_priority():
    try:
        conn = sqlite3.connect('time_management.db')
        cursor = conn.cursor()

        # Calculating total time spent on each task
        cursor.execute('''
            SELECT task, SUM(
                JULIANDAY(end_time) - JULIANDAY(start_time)
            ) as total_time
            FROM records
            GROUP BY task
            ORDER BY total_time DESC
        ''')
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def toggle_time_format():
    global time_format_24hr
    time_format_24hr = not time_format_24hr
    format_text = "24-hour" if time_format_24hr else "12-hour"
    print(f"Switched to {format_text} format.")


def daily_summary(date=None):
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')

    try:
        conn = sqlite3.connect('time_management.db')
        cursor = conn.cursor()

        cursor.execute("SELECT task, start_time, end_time FROM records WHERE date = ?", (date,))
        records = cursor.fetchall()

        if not records:
            print(f"No activities recorded for {date}.")
            return

        print(f"Summary for {date}:")
        for task, start, end in records:
                start_formatted = format_time_for_display(start)
                end_formatted = format_time_for_display(end)
                print(f"Task: {task}, Start: {start_formatted}, End: {end_formatted}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def show_help():
    help_text = """
    Commands:
    - record DATE START_TIME END_TIME TASK TAG: Add a new record.
    - query QUERY: Search for records by date, task, or tag.
    - report START_DATE END_DATE: Generate a report between two dates.
    - priority: Show tasks sorted by total time spent.
    - summary [DATE]: Show a summary of time usage for a specific date. If no date is provided, today's summary is shown.
    - help: Show this help message.
    - format: Toggle between 12-hour and 24-hour time formats.
    """
    print(help_text)
    
def convert_time_format(time_str):
    if time_format_24hr:
        # Assuming input in 24-hour format
        return time_str
    else:
        # Convert from 12-hour format to 24-hour format
        return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')

def convert_time_format(time_str):
    if time_format_24hr:
        # Assuming input in 24-hour format
        return time_str
    else:
        # Convert from 12-hour format to 24-hour format
        return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')

def convert_to_24hr_format(time_str):
    try:
        # Strip any leading/trailing whitespace
        time_str = time_str.strip()

        # Check if time string contains 'AM' or 'PM' (with or without a preceding space)
        if 'AM' in time_str.upper() or 'PM' in time_str.upper():
            # Add a space before 'AM' or 'PM' if it's missing
            time_str = time_str.replace('AM', ' AM').replace('PM', ' PM')

            # Convert from 12-hour format (with AM/PM) to 24-hour format
            return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')
        else:
            # Assume it's already in 24-hour format
            return time_str
    except ValueError as e:
        print(f"Error parsing time: {e}")

    
def format_time_for_display(time_str):
    # In 24-hour format mode, return the time as is
    if time_format_24hr:
        return time_str

    # Convert time from 24-hour to 12-hour format for display
    try:
        # Try converting from 24-hour format first
        formatted_time = datetime.strptime(time_str, '%H:%M').strftime('%I:%M %p')
    except ValueError:
        # If it fails, the time might already be in 12-hour format
        formatted_time = time_str

    return formatted_time



def main():
    global time_format_24hr
    create_database()

    while True:
        command = input("Enter your command: ")
        parts = command.split()
        action = parts[0].lower()

        if action == 'help':
            show_help()
        elif action == 'format':
            toggle_time_format()
        elif command.lower().startswith('record'):
            parts = command.split(maxsplit=4)
            if len(parts) == 5:
                _, date_str, start_time, end_time, rest = parts
                task_tag = rest.rsplit(' ', 1)
                if len(task_tag) == 2:
                    task, tag = task_tag
                else:
                    print("Invalid record format. Task and tag should be separated.")
                    continue

                task = task.strip('‘’')
                date = parse_date(date_str)
                add_record(date, start_time, end_time, task, tag)
                print("Record added successfully.")
            else:
                print("Invalid record format. Please use 'record DATE FROM TO 'TASK' TAG'.")
        elif action == 'query':
            _, query = parts
            records = query_records(query)
            for record in records:
                print(record)
        elif action == 'report':
            if len(parts) == 3:
                _, start_date, end_date = parts
                records = generate_report(start_date, end_date)
                for record in records:
                    print(record)
            else:
                print("Invalid report format. Please use 'report START_DATE END_DATE'.")
        elif action == 'priority':
            records = get_activity_priority()
            for record in records:
                print(f"Task: {record[0]}, Total Time: {record[1]}")
        else:
            print("Invalid action. Please start with 'record', 'query', 'report', or 'priority'.")


if __name__ == "__main__":
    main()
