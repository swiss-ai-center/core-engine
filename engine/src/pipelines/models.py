from typing import List

from pydantic.main import BaseModel
from .enums import NodeType
from common.models import APIDescription


class Node(BaseModel):
    id: str
    type: NodeType | None
    input: dict | None
    params: dict | None
    next: List[str] = []
    ready: str | None
    before: str | None
    after: str | None
    api: APIDescription | None
    url: str | None


class PipelineModel(BaseModel):
    id: int
    url: str
    api: APIDescription
