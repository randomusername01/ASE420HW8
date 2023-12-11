import pytest
import sys
sys.path.append("../")
from ver_1 import add_record, create_database, convert_to_24hr_format, query_records

# Setup for the tests
@pytest.fixture(scope="module")
def setup_database():
    create_database()
    yield

def test_add_record_valid(setup_database):
    add_record('2023-01-01', '09:00', '17:00', 'Test Task', 'Work')

def test_add_record_invalid_time_format(setup_database, capsys):
    add_record('2023-01-01', '9 AM', '5 PM', 'Test Task', 'Work')
    captured = capsys.readouterr()
    assert "Database error" in captured.out

def test_query_records_valid(setup_database):
    result = query_records('2023-01-01')

def test_query_records_invalid(setup_database):
    result = query_records('invalid-date')

def test_convert_to_24hr_format():
    result = convert_to_24hr_format('2:30 PM')
    assert result == '14:30', "Conversion to 24-hour format failed"

