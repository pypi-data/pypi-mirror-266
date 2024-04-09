import pytest
from ..lib.MsServerSQL import SQLServerDatabase

# Fixture to set up a test SQLServerDatabase instance
@pytest.fixture
def test_db():
    db = SQLServerDatabase(
        sql_server="test_server",
        database="test_database",
        username="test_username",
        password="test_password",
        table_name="test_table",
        columns_formatted=["col1", "col2"],
        columns_normal=["column1", "column2"]
    )
    yield db
    db.close_connection()

# Test case to check if a connection is established
def test_connection_established(test_db):
    assert test_db.connection is not None

# Test case to check select_data method
def test_select_data(test_db):
    # Insert some test data first
    test_data = [("value1", "value2"), ("value3", "value4")]
    insert_result = test_db.insert_data(test_data)
    assert insert_result["successful_rows"] == test_data

    # Select the inserted data
    query = f"SELECT * FROM {test_db.table_name}"
    result = test_db.select_data(query)
    
    # Check if the inserted data is retrieved correctly
    assert result == test_data

# Test case to check insert_data method
def test_insert_data(test_db):
    # Test data to insert
    test_data = [("value1", "value2")]

    # Insert the test data
    insert_result = test_db.insert_data(test_data)
    
    # Check if the insertion was successful
    assert insert_result["successful_rows"] == test_data

# Test case to check close_connection method
def test_close_connection(test_db):
    # Close the connection
    test_db.close_connection()
    
    # Check if the connection is closed
    assert test_db.connection.closed

