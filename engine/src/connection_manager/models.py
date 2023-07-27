from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from fastapi import WebSocket


class ExecutionType(str, Enum):
    PIPELINE = "pipeline"
    SERVICE = "service"


class Connection(BaseModel):
    websocket: WebSocket | None
    linked_id: UUID | None
    execution_type: ExecutionType | None

    class Config:
        arbitrary_types_allowed = True


class ConnectionData(BaseModel):
    linked_id: UUID | None
    execution_type: ExecutionType | None


class MessageType(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"


class MessageSubject(str, Enum):
    CONNECTION = "connection"
    EXECUTION = "execution"


class MessageData(BaseModel):
    text: str
    data: dict


class Message(BaseModel):
    message: MessageData
    type: MessageType
    subject: MessageSubject

    class Config:
        arbitrary_types_allowed = True
