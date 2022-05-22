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
	BRANCH = "branch"
	HTTP = "http"
	LOOP = "loop"
	LOOPEND = "loopend"

class StorageType(str, Enum):
	LOCAL = "local"
	S3 = "S3"

class DBType(str, Enum):
	MEMORY = "memory"
	MONGO = "mongo"

class TaskType(str, Enum):
	PROCESS = "process"
	ERROR = "error"
	RETRY = "retry"
