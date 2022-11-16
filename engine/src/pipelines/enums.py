from enum import Enum


class NodeType(str, Enum):
    NODE = "node"
    ENTRY = "entry"
    END = "end"
    SERVICE = "service"
    BRANCH = "branch"
    HTTP = "http"
    LOOP = "loop"
    LOOPEND = "loopend"
