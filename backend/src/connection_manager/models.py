from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from fastapi import WebSocket
from pydantic_settings import SettingsConfigDict


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
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    websocket: Optional[WebSocket] = None
    linked_id: Optional[UUID] = None
    execution_type: Optional[ExecutionType] = None


class ConnectionData(BaseModel):
    """
    ConnectionData is used to store the linked_id and the execution_type when sending a message to the client.
    """
    linked_id: Optional[UUID] = None
    execution_type: Optional[ExecutionType] = None


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
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    message: MessageData
    type: MessageType
    subject: MessageSubject


class MessageToSend(BaseModel):
    """
    MessageToSend is used to store the message and the linked_id in a queue to retry sending the message.
    """
    model_config = SettingsConfigDict(arbitrary_types_allowed=True)

    message: Message
    linked_id: UUID
