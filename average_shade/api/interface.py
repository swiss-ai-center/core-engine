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
        "route": "average-shade",
        "body": ["image"],
        "bodyType": ["[image/png, image/jpeg, image/jpg]"],
        "resultType": ["[application/json]"],
        "summary": "Returns the average shade of an image"
    }
