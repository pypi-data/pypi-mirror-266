import pysftp
import logging

class SFTPClient:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.sftp = None
    
    def connect(self):
        try:
            logging.info('Trying to connect to sftp')
            self.sftp = pysftp.Connection(self.hostname, port=self.port, username=self.username, password=self.password)
            logging.info("Connected to SFTP server")
        except Exception as e:
            logging.error(f"Error connecting to SFTP server: {e}")
    
    def upload_file(self, local_path, remote_path):
        try:
            logging.info(f'Uploading file from {local_path} to sftp {remote_path}')
            self.sftp.put(local_path, remote_path)
            logging.info(f"File uploaded successfully to {remote_path}")
        except Exception as e:
            logging.info(f"Error uploading file: {e}")
    
    def download_file(self, remote_path, local_path):
        try:
            logging.info(f'Downloading file from {remote_path} to sftp {local_path}')
            self.sftp.get(remote_path, local_path)
            logging.info(f"File downloaded successfully to {local_path}")
        except Exception as e:
            logging.info(f"Error downloading file: {e}")
    
    def close(self):
        if self.sftp:
            self.sftp.close()
            logging.info("Connection closed")

