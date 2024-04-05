import os
from dotenv import load_dotenv

load_dotenv()

sftp_config = {    "hostname": os.environ.get("hostname_sftp"),
"username": os.environ.get("username_sftp"),
"password": os.environ.get("password_sftp"),
"port": int(os.environ.get("port_sftp")),
"remote_directory": os.environ.get("remote_directory_sftp") , 

}  # Replace with your SFTP configurations
connection_config = {    "username":  os.environ.get("username_oracle"),
"password": os.environ.get("password_oracle"),
"host":  os.environ.get("host_oracle"),
"port":  os.environ.get("port_oracle"),
"service_name":  os.environ.get("service_name_oracle")}  # Replace with your Oracle configurations
azure_blob_config = {    "account_name": os.environ.get("account_name_az_blob_storage"),
"account_key": os.environ.get("account_key_az_blob_storage"),
"container_name": os.environ.get("container_name_az_blob_storage"),
"flow_name":os.environ.get("flow_name")}  # Replace with your Azure Blob Storage configurations
flow_config = {
    "table_name" : os.environ.get("table_name"),
    "flow_name" : os.environ.get("flow_name"),
    "primary_key" : os.environ.get("primary_key"),
     "regex_pattern" : os.environ.get("regex_pattern"),
     "date_fields" : os.environ.get('date_fields', '').split(',')
}

azure_table_config = {
    "account_key": os.environ.get("account_key_az_blob_storage"),
    "account_name": os.environ.get("account_name_az_blob_storage"),
    "flow_name":os.environ.get("flow_name"),
   
    
}

sql_server_config = {
    "sql_server" : os.environ.get("sql_server"),
    "username" :  os.environ.get("username_sqlserver") ,
    "database" : os.environ.get("database_sqlserver") ,
    "password" : os.environ.get("password_server")
}

