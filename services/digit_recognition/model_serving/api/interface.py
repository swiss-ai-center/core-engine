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
        "name": "Digit Recognition",
        "slug": "digit_recognition",
        "url": "digit-recognition",
        "summary": "Recognizes a digit in an image using mnist trained model",
        "description": "Recognizes a digit in an image using mnist trained model",
        "data_in_fields": [
            {
                "name": "image",
                "type": ["image/png", "image/jpeg", "image/jpg"],
            }
        ],
        "data_out_fields": [
            {
                "name": "result",
                "type": ["application/json"],
            }
        ],
    }
