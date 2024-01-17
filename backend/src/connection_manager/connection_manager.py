import json
from typing import List
from fastapi import WebSocket
from functools import lru_cache
from uuid import UUID
from connection_manager.models import Connection, ExecutionType, MessageSubject, MessageType, Message, MessageToSend, \
    ConnectionData
from common.exceptions import CouldNotSendJsonException


async def send_json_to_websocket(message: Message, websocket: WebSocket):
    await websocket.send_json(message.model_dump())


class MessageQueue:
    def __init__(self):
        self.queue: List[MessageToSend] = []

    def add(self, message: MessageToSend):
        self.queue.append(message)

    def get(self):
        return self.queue.pop(0)


class ConnectionManager:
    def __init__(
            self,
    ):
        self.active_connections: List[Connection] = []
        self.message_queue = MessageQueue()

    def find_by_linked_id(self, linked_id: UUID):
        for connection in self.active_connections:
            if str(connection.linked_id) == str(linked_id):
                return connection
        return None

    def find_by_websocket(self, websocket: WebSocket):
        for connection in self.active_connections:
            if connection.websocket == websocket:
                return connection
        return None

    def set_linked_id(self, websocket: WebSocket, linked_id: UUID):
        connection = self.find_by_websocket(websocket)
        if connection:
            connection.linked_id = linked_id
            return connection
        return None

    def set_execution_type(self, websocket: WebSocket, execution_type: ExecutionType):
        connection = self.find_by_websocket(websocket)
        if connection:
            connection.execution_type = execution_type
            return connection
        return None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        connection = Connection()
        connection.websocket = websocket
        self.active_connections.append(connection)
        connection_data = ConnectionData(linked_id=connection.linked_id, execution_type=connection.execution_type)
        message = Message(
            message={
                "text": "Connected to the backend's WebSocket",
                "data": connection_data.model_dump(),
            },
            type=MessageType.SUCCESS, subject=MessageSubject.CONNECTION
        )
        await send_json_to_websocket(message, connection.websocket)

    def disconnect(self, websocket: WebSocket):
        connection = self.find_by_websocket(websocket)
        if connection:
            self.active_connections.remove(connection)
            connection.websocket.close()

    async def send_string(self, message: str, linked_id: UUID):
        connection = self.find_by_linked_id(linked_id)
        if connection:
            await connection.websocket.send_text(message)

    async def send_json(self, message: Message, linked_id: UUID):
        connection = self.find_by_linked_id(linked_id)
        # Need to dump and load to avoid serialization issues
        json_dumped = json.dumps(message.model_dump(), default=str)
        json_object = json.loads(json_dumped)
        if connection:
            await connection.websocket.send_json(json_object)
        else:
            raise CouldNotSendJsonException(f"Could not send json to linked_id {linked_id}", message, linked_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)

    async def broadcast_json(self, message: Message):
        for connection in self.active_connections:
            await connection.websocket.send_json(message.model_dump())

    async def retry_send_message(self):
        while len(self.message_queue.queue) > 0:
            message_to_send = self.message_queue.get()
            try:
                await self.send_json(message_to_send.message, message_to_send.linked_id)
            except CouldNotSendJsonException:
                pass


@lru_cache()
def get_connection_manager():
    return ConnectionManager()
