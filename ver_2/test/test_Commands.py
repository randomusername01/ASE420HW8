import os
import sys
import pytest
import csv
from unittest.mock import MagicMock, Mock, patch
dir_path = os.path.dirname(os.path.realpath(__file__))
src_dir = os.path.join(dir_path, '..', 'src')
sys.path.append(src_dir)
from commands import AddRecordCommand, QueryCommand, ReportCommand, PriorityCommand, SummaryCommand, CommandInterpreter
from database import Database


@pytest.fixture
def mock_db():
    with patch('database.Database') as mock:
        mock_instance = mock.get_instance.return_value
        mock_instance.get_connection.return_value = Mock()
        yield mock_instance


def test_command_interpreter():
    interpreter = CommandInterpreter(True)
    assert interpreter.time_format_24hr == True

@pytest.fixture
def mock_db_connection():
    with patch.object(Database, 'get_instance') as mock_db:
        mock_conn = mock_db.return_value.get_connection.return_value
        mock_conn.cursor.return_value = MagicMock()
        yield mock_conn

def test_add_record_execute(mock_db_connection):
    command = AddRecordCommand('2023-01-01', '09:00', '17:00', 'Meeting', 'Work')
    command.execute()
    mock_db_connection.cursor().execute.assert_called_once_with(
        "INSERT INTO records (date, start_time, end_time, task, tag) VALUES (?, ?, ?, ?, ?)",
        ('2023-01-01', '09:00', '17:00', 'Meeting', 'Work')
    )

def test_query_command_execute(mock_db_connection):
    command = QueryCommand('Meeting', True)
    command.execute()
    mock_db_connection.cursor().execute.assert_called_once()
    args, kwargs = mock_db_connection.cursor().execute.call_args
    assert "SELECT * FROM records WHERE" in args[0]

def test_report_command_execute(mock_db_connection):
    command = ReportCommand('2023-01-01', '2023-01-31')
    command.execute()
    mock_db_connection.cursor().execute.assert_called_once_with(
        "SELECT * FROM records WHERE date BETWEEN ? AND ?", ('2023-01-01', '2023-01-31')
    )

def test_report_command_export_to_csv(mock_db_connection, tmp_path):
    command = ReportCommand('2023-01-01', '2023-01-31')
    filename = tmp_path / "report.csv"
    command.execute = MagicMock(return_value=[(1, '2023-01-01', '09:00', '17:00', 'Meeting', 'Work')])
    command.export_to_csv(filename)
    assert os.path.exists(filename)
    with open(filename) as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) > 1 
