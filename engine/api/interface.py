from typing import Optional, Union, List, Literal
from pydantic import BaseModel
from .Engine.Enums import NodeType
from enum import Enum

class ServiceType(str, Enum):
	SERVICE = "service"
	PIPELINE = "pipeline"

class JobResponse(BaseModel):
	jobId: str

class APIDescription(BaseModel):
	route: str
	summary: Optional[str]
	description: Optional[str]
	body: Union[str, dict, List[str]]

class Branch(BaseModel):
	exec: Optional[str]
	out: Optional[dict]
	next: Optional[List[str]]

class Node(BaseModel):
	id: str
	type: Optional[NodeType]
	input: Optional[dict]
	params: Optional[dict]
	next: List[str] = []
	ready: Optional[str]
	before: Optional[str]
	after: Optional[str]
	api: Optional[APIDescription]
	url: Optional[str]

class PipelineDescription(BaseModel):
	nodes: List[dict]
	type: Literal[ServiceType.PIPELINE]

class ServiceDescription(BaseModel):
	url: str
	api: APIDescription
	type: Literal[ServiceType.SERVICE]
