from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
import logging
from datetime import datetime

class AzureDataTablesClient:
    def __init__(self, connection_string, table_name):
        self.connection_string = connection_string
        self.table_name = table_name
        self.table_service_client = None

    def connect(self):
        try:
            logging.info('Trying to connect to Azure Data Tables')
            self.table_service_client = TableServiceClient.from_connection_string(self.connection_string)
            logging.info("Connected to Azure Data Tables")
        except Exception as e:
            logging.error(f"Error connecting to Azure Data Tables: {e}")

    def insert_batch_entities(self, entities,PartitionKey, RowKey,columnstoinsert, batch_size=1):
        try : 
            logging.info(f'Preparing data to insert into {self.table_name} table')
            table_client = self.table_service_client.get_table_client(self.table_name)
            entities_to_insert = []
            for _,row in entities.iterrows():
                entity = {'PartitionKey': PartitionKey, 'RowKey': row[RowKey]}
                for col in columnstoinsert:
                    entity[col] = row[col]
                entities_to_insert.append(("upsert", entity))
                if len(entities_to_insert) == batch_size : 
                     logging.info(f'batch to insert : {entities_to_insert}')
                     table_client.submit_transaction(entities_to_insert)
                     entities_to_insert = []
            if len(entities_to_insert) > 0 : 
                logging.info(f'batch to insert : {entities_to_insert}')
                table_client.submit_transaction(entities_to_insert)
                
            logging.info(f'All lines are successfully inserted into {self.table_name} table.')

        except ValueError as e : 
             logging.error(f'An error was occured while trying to insert data into {self.table_name} table : {e}')

    def query_entities(self,filter_condition,batch_size=1):
        try:

            table_client = self.table_service_client.get_table_client(self.table_name)
            entities = []
            logging.info(f'Executing query : {filter_condition}')
            for entity_page in table_client.query_entities(query_filter=filter_condition, results_per_page=batch_size).by_page():
                entities.extend(list(entity_page))
                break
            logging.info(f'Query Results : {entities}')
            return entities
        except ValueError as e:
            logging.error(f'An error occured while trying to query data from {self.table_name} table : {e}')
            


