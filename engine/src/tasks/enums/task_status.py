from enum import Enum


class TaskStatus(str, Enum):
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    NA = "unavailable"
