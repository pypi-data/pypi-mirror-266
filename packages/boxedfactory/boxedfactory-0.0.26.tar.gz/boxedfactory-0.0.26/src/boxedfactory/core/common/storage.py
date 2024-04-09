import os
import time
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from .configurations import Configuration, Configurable

class AzureBlobStorageService(Configurable):
    def __init__(self, config: Configuration) -> None:
        Configurable.__init__(self, config)
        self.account_name = self.config.get_value("azure_blob_storage:account:name")
        self.account_key = self.config.get_value("azure_blob_storage:account:key")
        self.container_name = self.config.get_value("azure_blob_storage:container")
        self.protocol = self.config.get_value("azure_blob_storage:default_endpoints_protocol")
        self.endpoint = self.config.get_value("azure_blob_storage:blob_endpoint")

    def get_azure_connection_string(self):
        parameters = {
            "AccountName": self.account_name,
            "AccountKey": self.account_key,
            "DefaultEndpointsProtocol": self.protocol,
            "BlobEndpoint": self.endpoint
        }
        return "".join([f"{i}={parameters[i]};" for i in parameters]), self.container_name
    
    def ensure_container(self, blob_service_client:BlobServiceClient, container_name:str):
        try:
            with blob_service_client.create_container(container_name) as container:
                pass
        except Exception as e:
            pass    

    def upload_file(self, content:bytes, path:str = None):
        path = path or self.get_unique_path()
        connection_string, container_name = self.get_azure_connection_string()
        with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
            self.ensure_container(blob_service_client, container_name)
            with blob_service_client.get_blob_client(container=container_name, blob=path) as client:
                client.upload_blob(content)
                return path
            
    def download_file(self, path:str) -> bytes:
        connection_string, container_name = self.get_azure_connection_string()
        with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
            self.ensure_container(blob_service_client, container_name)
            with blob_service_client.get_blob_client(container=container_name, blob=path) as client:
                return client.download_blob()

    def delete_file(self, path:str):
        connection_string, container_name = self.get_azure_connection_string()
        with BlobServiceClient.from_connection_string(connection_string) as blob_service_client:
            self.ensure_container(blob_service_client, container_name)
            with blob_service_client.get_blob_client(container=container_name, blob=path) as client:
                return client.delete_blob()
        
    def get_unique_path(self, sep:str = '/'):
        gm = time.gmtime()
        id = str(uuid.uuid4()).replace("-", "").lower()
        return sep.join([str(i) for i in [gm.tm_year, gm.tm_mon, gm.tm_mday, gm.tm_hour, id]])