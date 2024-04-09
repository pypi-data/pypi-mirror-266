import os
from dotenv import load_dotenv

load_dotenv()

env_variables = [
    "hostname_sftp", "username_sftp", "password_sftp", "port_sftp", "remote_directory_sftp",
    "username_oracle", "password_oracle", "host_oracle", "port_oracle", "service_name_oracle",
    "account_name_az_blob_storage", "account_key_az_blob_storage", "container_name_az_blob_storage", "flow_name",
    "table_name", "primary_key", "regex_pattern", "date_fields", "sql_server", "username_sqlserver",
    "database_sqlserver", "password_server"
]

def test_env_variables_exist():
    missing_variables = []

    for var in env_variables:
        if os.getenv(var) is None:
            missing_variables.append(var)

    assert not missing_variables, f"Missing environment variables: {missing_variables}"