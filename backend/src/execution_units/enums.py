from enum import Enum


class ExecutionUnitStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    SLEEPING = "sleeping"


# class ExecutionUnitType(Enum):
#     PIPELINE = "pipeline"
#     SERVICE = "service"
#     EXECUTION_UNIT = "execution_unit"
