# main.py
import sys
sys.path.append('src')
from commands import CommandInterpreter, show_help
from database import Database
from formatTime import toggle_time_format, convert_to_24hr_format, format_time_for_display, parse_date

time_format_24hr = True


def main():
    Database.get_instance() 
    Database.create_database() 
    global time_format_24hr

    show_help()

    command_interpreter = CommandInterpreter(time_format_24hr)

    while True:
        command = input("Enter your command: ")
        result = command_interpreter.interpret_and_execute(command)
        if result == 'exit':
            break

if __name__ == "__main__":
    main()