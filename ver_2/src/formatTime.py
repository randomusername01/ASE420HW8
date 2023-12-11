from datetime import datetime

def toggle_time_format(time_format_24hr):
    time_format_24hr = not time_format_24hr
    format_text = "24-hour" if time_format_24hr else "12-hour"
    print(f"Switched to {format_text} format.")
    return time_format_24hr

def convert_to_24hr_format(time_str, time_format_24hr):
    if not time_format_24hr and ('AM' in time_str.upper() or 'PM' in time_str.upper()):
        try:
            return datetime.strptime(time_str.strip(), '%I:%M %p').strftime('%H:%M')
        except ValueError as e:
            print(f"Error parsing time: {e}")
    return time_str

def format_time_for_display(time_str, time_format_24hr):
    if 'AM' in time_str.upper() or 'PM' in time_str.upper():
        if time_format_24hr:
            return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')
        else:
            return time_str
    else:
        if time_format_24hr:
            return time_str
        else:
            try:
                return datetime.strptime(time_str, '%H:%M').strftime('%I:%M %p')
            except ValueError:
                return time_str

        
def parse_date(date_str):
    if date_str.lower() == 'today':
        return datetime.today().strftime('%Y-%m-%d')
    return date_str