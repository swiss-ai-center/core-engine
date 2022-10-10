from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

class TaskId(BaseModel):
	task_id: str

def engineAPI():
	return {"route": "face-analyze", "body": ["image"], "bodyType": ["[image/png, image/jpeg, image/jpg]"], "summary": "Guess age, gender, emotion and race of a face found in the provided image"}
