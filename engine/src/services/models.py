from pydantic.main import BaseModel

from common.models import APIDescription


class ServiceModel(BaseModel):
    id: int
    url: str
    api: APIDescription
