from enum import Enum


class Status(str, Enum):
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    NA = "unavailable"
