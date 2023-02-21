from abc import ABCMeta, abstractmethod
from typing import List, TypedDict
from pydantic import BaseModel
from .enums import FieldDescriptionType, ServiceStatus


class FieldDescription(TypedDict):
    """
    Field description model
    """
    name: str
    type: List[FieldDescriptionType]


class Service(BaseModel, metaclass=ABCMeta):
    """
    Service model
    """

    name: str
    slug: str
    url: str
    summary: str
    description: str | None
    status: ServiceStatus
    data_in_fields: List[FieldDescription] | None
    data_out_fields: List[FieldDescription] | None

    def get_data_in_fields(self):
        """
        Data in fields
        """
        return self.data_in_fields

    def get_data_out_fields(self):
        """
        Data out fields
        """
        return self.data_out_fields

    @abstractmethod
    async def process(self, data):
        pass
