from enum import Enum


class PipelineElementType(Enum):
    SERVICE = "service"
    BRANCH = "branch"
    WAIT = "wait"
    LOOP = "loop"
