import pytest
from ..lib.TableStorage import AzureDataTablesClient
import logging
import os

@pytest.fixture
def azure_tables_client():
    connection_string = os.environ.get('AZURE_TABLES_CONNECTION_STRING')
    table_name = 'test'
    logging.warning(connection_string)
    return AzureDataTablesClient(connection_string, table_name)

def test_connect(azure_tables_client):
    azure_tables_client.connect()
    assert azure_tables_client.table_service_client is not None

def test_insert_and_query_entities(azure_tables_client):
    # Define your test data here
    test_entities = [
        {"PartitionKey": "part_key_1", "RowKey": "row_key_1", "col1": "value1", "col2": "value2"},
        {"PartitionKey": "part_key_2", "RowKey": "row_key_2", "col1": "value3", "col2": "value4"}
    ]

    # Insert test entities
    azure_tables_client.connect()
    azure_tables_client.insert_batch_entities(test_entities, PartitionKey="PartitionKey", RowKey="RowKey", columnstoinsert=["col1", "col2"])

    # Query inserted entities
    entities = azure_tables_client.query_entities(filter_condition="PartitionKey eq 'PartitionKey'")
    
    # Check if the inserted entities are retrieved correctly
    assert len(entities) == 1
    assert entities[0]["PartitionKey"] == "PartitionKey"
    assert entities[0]["RowKey"] == "row_key_1"
    assert entities[0]["col1"] == "value1"
    assert entities[0]["col2"] == "value2"


