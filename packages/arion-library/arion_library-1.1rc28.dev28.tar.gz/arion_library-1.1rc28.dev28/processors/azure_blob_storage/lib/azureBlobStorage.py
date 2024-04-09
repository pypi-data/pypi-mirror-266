from azure.storage.blob import BlobServiceClient, ContainerClient
import re
from io import BytesIO
from datetime import datetime
import logging

class AzureBlobProcessor:
    """
    A class for processing files in Azure Blob Storage.
    
    :param account_name: The Azure Storage account name.
    :param account_key: The Azure Storage account key.
    :param container_name: The name of the container in Azure Blob Storage.
    :param flow_name: The name of the flow for organizing files.
    """

    def __init__(self, account_name, account_key, container_name, flow_name):
        """
        Initialize the AzureBlobProcessor.

        This method creates a connection to the Azure Blob Storage container.

        :param account_name: The Azure Storage account name.
        :param account_key: The Azure Storage account key.
        :param container_name: The name of the container in Azure Blob Storage.
        :param flow_name: The name of the flow for organizing files.
        """
        self.azure_blob_config = {"account_name": account_name, "account_key": account_key, "container": container_name, "flow_name": flow_name}
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.azure_blob_config['container'])

    def read_blob_files(self, regex_pattern=r'.*'):
        """
        Retrieve files from Azure Blob Storage.

        This method yields file name and content for each blob in the container matching the regex pattern.

        :param regex_pattern: A regular expression pattern for filtering blob names (default: '.*').
        """
        for blob in self.container_client.list_blobs():
            if re.match(regex_pattern, blob.name):
                blob_client = self.container_client.get_blob_client(blob.name)
                file_content = BytesIO()
                file_content.write(blob_client.download_blob().readall())
                file_content.seek(0)
                yield {'file_name': blob.name, 'file_content': file_content}

    def push_files_to_blob(self, files_info):
        """
        Push files to Azure Blob Storage.

        This method uploads files to the Azure Blob Storage container.

        :param files_info: A list of tuples containing file name and content.
        """
        for file_info in files_info:
            file_name = file_info[0]
            file_content = file_info[1]
            current_date = datetime.now().strftime("%d-%m-%Y")
            folder_name = f"{self.azure_blob_config['flow_name']}/{current_date}/"
            blob_name = folder_name + file_name
            self.container_client.upload_blob(name=blob_name, data=file_content, overwrite=True)
            logging.info(f"File '{file_name}' successfully pushed to Azure Blob Storage.")
