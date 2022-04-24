from pydantic import BaseModel

_uid = 0

def uid():
	global _uid
	_uid += 1
	return _uid

# Implement me!!!
# Define a meaningful input data object
# class Job(BaseModel):
# 	data1: str
# 	data2: str
# 	data3: int

class TaskId(BaseModel):
	task_id: str

# Also implement me!
# This is the custom API that will be sent to the Engine, with our magical (not completely defined yet) syntax
def engineAPI():
	return {"route":"faceDetection", "body":"image"}
