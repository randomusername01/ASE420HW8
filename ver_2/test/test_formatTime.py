import pytest
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
src_dir = os.path.join(dir_path, '..', 'src')
sys.path.append(src_dir)
from formatTime import toggle_time_format, convert_to_24hr_format, format_time_for_display, parse_date

from datetime import datetime

def test_toggle_time_format():
    assert toggle_time_format(True) == False
    assert toggle_time_format(False) == True

def test_convert_to_24hr_format():
    assert convert_to_24hr_format("2:30 PM", False) == "14:30"
    assert convert_to_24hr_format("14:30", True) == "14:30"

def test_format_time_for_display():
    assert format_time_for_display("2:30 PM", True) == "14:30"
    assert format_time_for_display("14:30", False) == "02:30 PM"

def test_parse_date():
    assert parse_date("today") == datetime.today().strftime('%Y-%m-%d')
    assert parse_date("2023-12-10") == "2023-12-10"
