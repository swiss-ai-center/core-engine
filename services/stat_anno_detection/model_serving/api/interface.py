from pydantic import BaseModel

_uid = 0


def uid():
    global _uid
    _uid += 1
    return _uid


class TaskId(BaseModel):
    task_id: str


def engineAPI():
    return {
        "route": "stat-anno-detection",
        "body": ["csv"],
        "bodyType": ["[text/csv]"],
        "resultType": ["[application/json]"],
        "summary": "Find anomalies in a time series"
    }
