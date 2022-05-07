from enum import Enum

class Status(str, Enum):
	RUNNING = "running"
	FINISHED = "finished"
	ERROR = "error"
	NA = "unavailable"

class NodeType(str, Enum):
	NODE = "node"
	ENTRY = "entry"
	END = "end"
	SERVICE = "service"

class StorageType(str, Enum):
	LOCAL = "local"
	S3 = "S3"

class DBType(str, Enum):
	MEMORY = "memory"
	MONGO = "mongo"
