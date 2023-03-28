from typing import TypedDict, List
from .enums import FieldDescriptionType


class FieldDescription(TypedDict):
    """
    Field description model
    """
    name: str
    type: List[FieldDescriptionType]
