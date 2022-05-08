from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

class TaskId(BaseModel):
	task_id: str

# Also implement me!
# This is the custom API that will be sent to the Engine, with our magical (not completely defined yet) syntax
def engineAPI():
	return {"route": "areaBlur", "body": ["image", "areas"]}
