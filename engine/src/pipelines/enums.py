from enum import Enum


class PipelineStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class PipelineElementType(Enum):
    SERVICE = "service"
    BRANCH = "branch"
    WAIT = "wait"
    LOOP = "loop"
