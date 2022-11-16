from pydantic import BaseModel

from common.models.api_description import APIDescription
from ..models.service import ServiceModel


class ServiceSchema(BaseModel):
    serviceId: int
    url: str
    api: APIDescription

    @staticmethod
    def toServiceSchema(service_model: ServiceModel):
        return ServiceSchema(serviceId=service_model.id)
