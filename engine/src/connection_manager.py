from enum import Enum
from typing import List
from fastapi import WebSocket
from functools import lru_cache
from uuid import UUID
from pydantic import BaseModel


class ExecutionType(str, Enum):
    PIPELINE = "pipeline"
    SERVICE = "service"


class Connection(BaseModel):
    websocket: WebSocket | None
    linked_id: UUID | None
    execution_type: ExecutionType | None

    class Config:
        arbitrary_types_allowed = True


class ConnectionManager:
    def __init__(
            self,
    ):
        self.active_connections: List[Connection] = []

    def find_by_linked_id(self, linked_id: UUID):
        for connection in self.active_connections:
            if connection.linked_id == linked_id:
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

    def set_execution_type(self, websocket: WebSocket, execution_type: ExecutionType):
        connection = self.find_by_websocket(websocket)
        if connection:
            connection.execution_type = execution_type

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        connection = Connection()
        connection.websocket = websocket
        self.active_connections.append(connection)
        await self.send_json_websocket({"message": f"Connected, data: {connection.dict()}"}, connection.websocket)

    def disconnect(self, websocket: WebSocket):
        connection = self.find_by_websocket(websocket)
        if connection:
            self.active_connections.remove(connection)
            connection.websocket.close()

    async def send_message(self, message: str, linked_id: UUID):
        connection = self.find_by_linked_id(linked_id)
        if connection:
            await connection.websocket.send_text(message)

    async def send_json(self, message: dict, linked_id: UUID):
        connection = self.find_by_linked_id(linked_id)
        if connection:
            await connection.websocket.send_json(message)

    async def send_json_websocket(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)

    async def broadcast_json(self, message: dict):
        for connection in self.active_connections:
            await connection.websocket.send_json(message)


@lru_cache()
def get_connection_manager():
    return ConnectionManager()
