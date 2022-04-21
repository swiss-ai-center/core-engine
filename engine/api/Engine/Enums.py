class Enum(object):
    pass

Status = Enum()
Status.RUNNING = "running"
Status.FINISHED = "finished"
Status.ERROR = "error"
Status.NA = "unavailable"

NodeType = Enum()
NodeType.NODE = "node"
NodeType.ENTRY = "entry"
NodeType.END = "end"
NodeType.SERVICE = "service"
