from pydantic.main import BaseModel

from common.models.api_description import APIDescription


class PipelineModel(BaseModel):
    id: int
    url: str
    api: APIDescription