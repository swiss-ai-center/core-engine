from datetime import datetime as Datetime
import os
from typing import List

from pymongo import MongoClient

class MongoDriver:
	database = None
	def __init__(
		self,
		username: str = "registry",
		password: str = "PiRegistry_2022",
		host: str = "localhost",
		port: int = 27017,
		databaseName: str = "Registry",
	):

		username = os.environ["MONGO_USERNAME"] if "MONGO_USERNAME" in os.environ else username
		password = os.environ["MONGO_PASSWORD"] if "MONGO_PASSWORD" in os.environ else password
		host = os.environ["MONGO_HOST"] if "MONGO_HOST" in os.environ else host
		port = int(os.environ["MONGO_PORT"]) if "MONGO_PORT" in os.environ else port
		databaseName = os.environ["MONGO_AUTHDB"] if "MONGO_AUTHDB" in os.environ else databaseName

		self.databaseName = databaseName
		print(host, port, databaseName)

		self.uri: str = (f"mongodb://{username}:{password}@{host}:{port}/{databaseName}")

		self.connection = self.open()

	def open(self):
		if self.database is None:
			print("Connection to mongoDB server...")
			self.connection: MongoClient = MongoClient(self.uri)
			self.database = self.connection[self.databaseName]
			print("Connection OK")

		return self.connection

	def get_collection(self, collectionName: str):
		if self.database is None:
			self.open()
		return self.database[collectionName]

	def close(self):
		self.connection.close()

