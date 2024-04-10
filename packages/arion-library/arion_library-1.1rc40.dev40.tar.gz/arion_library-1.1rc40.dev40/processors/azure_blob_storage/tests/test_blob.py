import pytest
from unittest.mock import Mock, patch
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from ..lib.azureBlobStorage import AzureBlobProcessor

@pytest.fixture
def mock_blob_service_client():
    return Mock(spec=BlobServiceClient)

@pytest.fixture
def mock_container_client():
    return Mock(spec=ContainerClient)

@pytest.fixture
def azure_blob_processor(mock_blob_service_client, mock_container_client):
    with patch('azure.storage.blob.BlobServiceClient.from_connection_string', return_value=mock_blob_service_client):
        with patch.object(mock_blob_service_client, 'get_container_client', return_value=mock_container_client):
            yield AzureBlobProcessor("test_account_name", "test_account_key", "test_container", "test_flow_name")

def test_azure_blob_processor_init(azure_blob_processor, mock_blob_service_client, mock_container_client):
    assert azure_blob_processor.blob_service_client == mock_blob_service_client
    assert azure_blob_processor.container_client == mock_container_client
    assert azure_blob_processor.azure_blob_config == {"account_name": "test_account_name", "account_key": "test_account_key", "container" :"test_container", "flow_name" : "test_flow_name"}

def test_read_blob_files(azure_blob_processor, mock_container_client):
    mock_blob = Mock()
    mock_blob.name = "test_blob_name.txt"
    mock_blob_client = Mock()
    mock_blob_client.download_blob.return_value.readall.return_value = b"Test Blob Content"
    mock_container_client.list_blobs.return_value = [mock_blob]

    with patch.object(mock_container_client, 'get_blob_client', return_value=mock_blob_client):
        files = list(azure_blob_processor.read_blob_files())

    assert len(files) == 1
    assert files[0]['file_name'] == "test_blob_name.txt"
    assert files[0]['file_content'].read() == b"Test Blob Content"

def test_push_files_to_blob(azure_blob_processor, mock_container_client):
    mock_file_info = ("test_file.txt", b"Test File Content")
    azure_blob_processor.push_files_to_blob([mock_file_info])

    mock_container_client.upload_blob.assert_called_once_with(name="test_flow_name/21-03-2024/test_file.txt", data=mock_file_info[1], overwrite=True)
