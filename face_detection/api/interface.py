from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

class TaskId(BaseModel):
	task_id: str

def engineAPI():
	return {"route": "face-detect", "body": ["image"], "bodyType": ["[image/png, image/jpeg, image/jpg]"], "summary": "Detect all faces in the provided image and returns their bounding box"}
