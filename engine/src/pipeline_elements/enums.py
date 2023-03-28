from enum import Enum


class PipelineElementType(Enum):
    SERVICE = "service"
    BRANCH = "branch"
    START = "start"
    END = "end"

