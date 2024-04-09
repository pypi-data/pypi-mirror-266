import pytest
from ..lib.sftp import SFTPClient
import logging
import os




@pytest.fixture
def sftp_client():
    hostname = os.environ.get('SFTP_HOST')
    port = int(os.environ.get('SFTP_PORT'))
    username = os.environ.get('SFTP_USERNAME')
    password = os.environ.get('SFTP_PASSWORD')
    return SFTPClient(hostname, port, username, password)

def test_connect(sftp_client):
    sftp_client.connect()
    assert sftp_client.sftp is not None

def test_upload_and_download(sftp_client):
    local_path = 'test_file.txt'
    remote_path = '/get/test_file.txt'

    # Upload file
    sftp_client.connect()
    sftp_client.upload_file(local_path, remote_path)

    # Download file
    download_path = 'downloaded_test_file.txt'
    sftp_client.download_file(remote_path, download_path)

    # Check if file exists
    assert os.path.isfile(download_path)

    # Clean up
    os.remove(download_path)

def test_close_connection(sftp_client):
    sftp_client.connect()
    sftp_client.close()
    assert sftp_client.sftp is None