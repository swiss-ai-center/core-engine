from enum import Enum


class PipelineElementType(Enum):
    SERVICE = "service"
    BRANCH = "branch"
    WAIT = "wait"


class InOutType(Enum):
    IN = "in"
    OUT = "out"
