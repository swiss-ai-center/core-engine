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
        "route": "ae-anno-detection",
        "body": ["text"],
        "bodyType": ["[text/csv, text/plain]"],
        # "bodyType": ["[application/json]"],
        # "bodyType": ["[image/png, image/jpeg]"],
        # "resultType": ["[application/json]"],
        "resultType": ["[image/png, image/jpeg]"],
        # "resultType": ["[multipart/form-data]"],
        "summary": "Find anomalies in a time series with autoencoder",
    }
