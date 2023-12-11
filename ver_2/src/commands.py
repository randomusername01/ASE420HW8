from datetime import datetime
from formatTime import format_time_for_display, convert_to_24hr_format, parse_date, toggle_time_format
from database import Database
import re
import csv

class Command:
    def execute(self):
        raise NotImplementedError

class AddRecordCommand(Command):
    def __init__(self, date, start_time, end_time, task, tag):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.task = task
        self.tag = tag

    def execute(self):
        conn = Database.get_instance().get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (date, start_time, end_time, task, tag) VALUES (?, ?, ?, ?, ?)",
                       (self.date, self.start_time, self.end_time, self.task, self.tag))
        conn.commit()

class QueryCommand(Command):
    def __init__(self, query, time_format_24hr):
        self.query = query
        self.time_format_24hr = time_format_24hr

    def execute(self):
        conn = Database.get_instance().get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE date = ? OR LOWER(task) LIKE ? OR LOWER(tag) LIKE ?",
                       (self.query, '%' + self.query.lower() + '%', '%' + self.query.lower() + '%'))
        records = cursor.fetchall()

        formatted_records = []
        for record in records:
            id, date, start_time, end_time, task, tag = record
            start_time_formatted = format_time_for_display(start_time, self.time_format_24hr)
            end_time_formatted = format_time_for_display(end_time, self.time_format_24hr)
            formatted_records.append((id, date, start_time_formatted, end_time_formatted, task, tag))

        return formatted_records

class ReportCommand(Command):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def execute(self):
        conn = Database.get_instance().get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE date BETWEEN ? AND ?", (self.start_date, self.end_date))
        return cursor.fetchall()
    
    def export_to_csv(self, filename):
        records = self.execute()
        with open(filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['ID', 'Date', 'Start Time', 'End Time', 'Task', 'Tag'])
            csv_writer.writerows(records)

class PriorityCommand(Command):
    def execute(self):
        conn = Database.get_instance().get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task, SUM(
                JULIANDAY(end_time) - JULIANDAY(start_time)
            ) as total_time
            FROM records
            GROUP BY task
            ORDER BY total_time DESC
        ''')
        return cursor.fetchall()

class SummaryCommand(Command):
    def __init__(self, date=None):
        if date is None:
            date = datetime.today().strftime('%Y-%m-%d')
        self.date = date

    def execute(self):
        conn = Database.get_instance().get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT task, start_time, end_time FROM records WHERE date = ?", (self.date,))
        return cursor.fetchall()

class CommandInterpreter:
    def __init__(self, time_format_24hr):
        self.time_format_24hr = time_format_24hr
        self.memento_stack = []

    def interpret_and_execute(self, command_str):
        parts = command_str.split()
        action = parts[0].lower()

        if action == 'record':
            self._handle_record(command_str)
        elif action == 'query':
            self._handle_query(parts[1:])
        elif action == 'report':
            self._handle_report(command_str)
        elif action == 'priority':
            self._handle_priority()
        elif action == 'summary':
            self._handle_summary(command_str)
        elif action == 'format':
            self._handle_format()
        elif action == 'help':
            show_help()
        elif action == 'exit':
            return 'exit'
        else:
            print("Invalid command. Type 'help' to see available commands.")

    def _handle_record(self, command_str):
        match = re.match(r'record (\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2} ?(?:AM|PM)?) (\d{1,2}:\d{2} ?(?:AM|PM)?) (.+)', command_str, re.IGNORECASE)
        if not match:
            print("Invalid record format.")
            return

        date_str, start_time, end_time, task_and_tag = match.groups()
        task_and_tag_parts = task_and_tag.rsplit(' ', 1)
        task = task_and_tag_parts[0].strip("'")
        tag = task_and_tag_parts[1] if len(task_and_tag_parts) > 1 else None

        start_time_24hr = convert_to_24hr_format(start_time, self.time_format_24hr)
        end_time_24hr = convert_to_24hr_format(end_time, self.time_format_24hr)

        add_record_cmd = AddRecordCommand(parse_date(date_str), start_time_24hr, end_time_24hr, task, tag)
        add_record_cmd.execute()
        print("Record added successfully.")

    def _handle_query(self, query_parts):
        query_cmd = QueryCommand(' '.join(query_parts), self.time_format_24hr)
        records = query_cmd.execute()
        for record in records:
            id, date, start_time, end_time, task, tag = record
            start_formatted = format_time_for_display(start_time, self.time_format_24hr)
            end_formatted = format_time_for_display(end_time, self.time_format_24hr)
            print(f"{id}, {date}, {start_formatted}, {end_formatted}, {task}, {tag}")

    def _handle_report(self, command_str):
        match = re.match(r'report (\d{4}-\d{2}-\d{2}) (\d{4}-\d{2}-\d{2})', command_str)
        if not match:
            print("Invalid report format.")
            return

        start_date, end_date = match.groups()
        report_cmd = ReportCommand(start_date, end_date)
        records = report_cmd.execute()
        for record in records:
            id, date, start_time, end_time, task, tag = record
            start_formatted = format_time_for_display(start_time, self.time_format_24hr)
            end_formatted = format_time_for_display(end_time, self.time_format_24hr)
            print(f"{id}, {date}, {start_formatted}, {end_formatted}, {task}, {tag}")

        csv_filename = f"report_{start_date}_{end_date}.csv"
        report_cmd.export_to_csv(csv_filename)
        print(f"Report exported to {csv_filename}")

    def _handle_priority(self):
        priority_cmd = PriorityCommand()
        records = priority_cmd.execute()
        for record in records:
            task, total_time = record
            print(f"Task: {task}, Total Time: {total_time}")

    def _handle_summary(self, command_str):
        match = re.match(r'summary(?: (\d{4}-\d{2}-\d{2}))?', command_str)
        date = match.group(1) if match else None
        summary_cmd = SummaryCommand(date)
        records = summary_cmd.execute()
        for record in records:
            task, start_time, end_time = record
            start_formatted = format_time_for_display(start_time, self.time_format_24hr)
            end_formatted = format_time_for_display(end_time, self.time_format_24hr)
            print(f"Task: {task}, Start: {start_formatted}, End: {end_formatted}")

    def _handle_format(self):
        self.time_format_24hr = toggle_time_format(self.time_format_24hr)
        format_text = "24-hour" if self.time_format_24hr else "12-hour"

def show_help():
    help_text = """
    Commands:
    - record DATE START_TIME END_TIME TASK TAG: Add a new record.
    - query QUERY: Search for records by date, task, or tag.
    - report START_DATE END_DATE: Generate a report between two dates.
    - priority: Show tasks sorted by total time spent.
    - summary [DATE]: Show a summary of time usage for a specific date.
    - help: Show this help message.
    - format: Toggle between 12-hour and 24-hour time formats.
    - exit: Exit the application.
    """
    print(help_text)