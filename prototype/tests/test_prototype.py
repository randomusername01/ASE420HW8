import pytest
import sqlite3
from datetime import datetime
import sys
sys.path.append('../')
from prototype import create_database, add_record, query_records  # Replace with the actual name of your module

# Constants
TEST_DB = 'test_time_management.db'

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Setup the test database
    create_database(TEST_DB)
    yield
    # Teardown code: remove the test database if necessary

def run_query(query, database=TEST_DB):
    """Helper function to run queries against the test database."""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def test_add_record():
    # Test add_record function
    date = datetime.today().strftime('%Y-%m-%d')
    add_record(date, '09:00', '10:00', 'Test Task', 'TestTag', database=TEST_DB)
    result = run_query(f"SELECT * FROM records WHERE date = '{date}'", TEST_DB)
    assert len(result) == 1
    assert result[0][2:6] == (date, '09:00', '10:00', 'Test Task')

def test_query_records():
    # Test query_records function
    tag_query = 'TestTag'
    result = query_records(tag_query, database=TEST_DB)
    assert len(result) >= 1
    assert any(tag_query in record for record in result)
