from enum import Enum


class PipelineStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class FieldDescriptionType(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_OGG = "audio/ogg"
