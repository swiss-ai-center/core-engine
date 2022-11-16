from typing import List

from pydantic.main import BaseModel
from engine.src.pipelines.enums.node_type import NodeType


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