from typing import List, TypedDict

from pydantic import BaseModel

from .enums import FieldDescriptionType


class FieldDescription(TypedDict):
    """
    Field description model
    """
    name: str
    type: List[FieldDescriptionType]


class Service(BaseModel):
    """
    Service model
    """

    name: str
    slug: str
    url: str
    summary: str
    description: str | None
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


class DigitRecognitionService(Service):
    """
    Digit recognition service model
    """

    def __init__(self):
        super().__init__(
            name="Digit recognition",
            slug="digit-recognition",
            url="http://digit-recognition:8001",
            summary="Digit recognition service",
            description="Digit recognition service",
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_JPG, FieldDescriptionType.IMAGE_PNG,
                                                     FieldDescriptionType.IMAGE_JPEG]),
            ],
            data_out_fields=[
                FieldDescription(name="digit", type=[FieldDescriptionType.TEXT_PLAIN]),
            ]
        )
