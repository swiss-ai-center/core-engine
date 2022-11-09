from typing import Optional, Union, List, Literal
from pydantic import BaseModel
from .Engine.Enums import NodeType, ServiceType

class JobResponse(BaseModel):
	jobId: str

class APIDescription(BaseModel):
	route: str
	summary: Optional[str]
	description: Optional[str]
	body: Union[str, dict, List[str]]
	bodyType: Optional[Union[str, List[str]]]
	resultType : Optional[Union[str, List[str]]]

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
	type: Union[Literal[ServiceType.PIPELINE], Literal[ServiceType.SERVICE]]

class ServiceDescription(BaseModel):
	url: str
	api: APIDescription
	type: Union[Literal[ServiceType.PIPELINE], Literal[ServiceType.SERVICE]]
