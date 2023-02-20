from enum import Enum


class ServiceStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class FieldDescriptionType(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    APPLICATION_JSON = "application/json"
