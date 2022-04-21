from typing import Optional, Union
from pydantic import BaseModel

class JobResponse(BaseModel):
	jobId : str

class APIDescription(BaseModel):
	route: str
	body: Union[str, dict]
	params: Optional[dict]

class ServiceDescription(BaseModel):
	url: str
	api: APIDescription
