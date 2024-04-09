from __future__ import annotations

import os
from typing import Optional

import pymongo
from dotenv import load_dotenv
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBConnector:
    def __init__(self, connection_string: Optional[str] = None):
        if not connection_string:
            connection_string = self._load_connection_string_from_env()
        if not connection_string:
            raise ValueError("Please specify MongoDB Connection string by passing it as an argument or setting it in the environment variable: MONGODB_CONNECTION_STRING")
        self._connection_string: str = connection_string
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
    @property
    def is_connected(self) -> bool:
        return self.client is not None

    @property
    def is_database_setup(self) -> bool:
        return self.database is not None
    
    def select_database(self, database_name: str) -> None:
        if not self.is_connected:
            raise ConnectionFailure("Please connect to MongoDB first.")
        self.database = self.client[database_name]
       
    def connect(self) -> None:
        if self.is_connected:
            return
        try:
            self.client = pymongo.MongoClient(self._connection_string)
        except ConnectionFailure as e:
            self.client = None
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")
        except Exception as e:
            self.client = None
            raise Exception(f"Failed to connect to MongoDB for unknown reason: {e}")

    def disconnect(self) -> None:
        if not self.is_connected:
            return
        if self.client is not None:
            self.client.close()
            self.client = None

    def _load_connection_string_from_env(self) -> str:
        load_dotenv()
        return os.getenv("MONGODB_CONNECTION_STRING")
        
    def __enter__(self) -> MongoDBConnector:
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()


__all__ = [
    "MongoDBConnector",
]
