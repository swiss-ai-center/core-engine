from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

class TaskId(BaseModel):
	task_id: str

def engineAPI():
	return {"route": "digit-recognition", "body": "image", "summary": "Recognizes a digit in an image using mnist trained model"}
