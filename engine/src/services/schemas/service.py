from pydantic import BaseModel

from common.models.api_description import APIDescription
from ..models.service import ServiceModel


class ServiceSchema(BaseModel):
    service_id: int
    url: str
    api: APIDescription

    @staticmethod
    def toServiceSchema(service_model: ServiceModel):
        return ServiceSchema(service_id=service_model.id)
