from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from fastapi import WebSocket


class ExecutionType(str, Enum):
    """
    ExecutionType is used to identify the type of execution that is being performed.
    """
    PIPELINE = "pipeline"
    SERVICE = "service"


class Connection(BaseModel):
    """
    Connection is used to store the WebSocket connection, the linked_id and the execution_type.
    """
    websocket: WebSocket | None
    linked_id: UUID | None
    execution_type: ExecutionType | None

    class Config:
        arbitrary_types_allowed = True


class ConnectionData(BaseModel):
    """
    ConnectionData is used to store the linked_id and the execution_type when sending a message to the client.
    """
    linked_id: UUID | None
    execution_type: ExecutionType | None


class MessageType(str, Enum):
    """
    MessageType is used to identify the type of message that is being sent.
    """
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"


class MessageSubject(str, Enum):
    """
    MessageSubject is used to identify the subject of the message that is being sent.
    """
    CONNECTION = "connection"
    EXECUTION = "execution"


class MessageData(BaseModel):
    """
    MessageData is used to store the text and the data when sending a message to the client.
    The data is of type ConnectionData but converted to dict.
    """
    text: str
    data: dict


class Message(BaseModel):
    """
    Message is used to store the message, the type and the subject when sending a message to the client.
    """
    message: MessageData
    type: MessageType
    subject: MessageSubject

    class Config:
        arbitrary_types_allowed = True


class MessageToSend(BaseModel):
    """
    MessageToSend is used to store the message and the linked_id in a queue to retry sending the message.
    """
    message: Message
    linked_id: UUID

    class Config:
        arbitrary_types_allowed = True