from typing import TypeVar, Callable

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from .configurations import Configuration, Configurable

T =  TypeVar("T")

ConnectionCallback = Callable[[Database,], T]
CollectionCallback = Callable[[Collection,], T]

class MongoService(Configurable):
    def __init__(self, config: Configuration) -> None:
        Configurable.__init__(self, config)
        self.host = self.config.get_value("mongo:host")
        self.port = self.config.get_value("mongo:port")
        self.username = self.config.get_value("mongo:credentials:username")
        self.password = self.config.get_value("mongo:credentials:password")

    def get_mongo_connection_string(self):
        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"

    def connection(self, database_name:str, callback:ConnectionCallback) -> T:
        with MongoClient(self.get_mongo_connection_string()) as client:
            database = client[database_name]
            return callback(database)

    def collection(self, database_name:str, collection_name:str, callback:CollectionCallback) -> T:
        with MongoClient(self.get_mongo_connection_string()) as client:
            database = client[database_name]
            collection = database[collection_name]
            return callback(collection)
