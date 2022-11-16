from pydantic import BaseModel
from ..models.task import TaskModel


class TaskSchema(BaseModel):
	taskId: int

	@staticmethod
	def toTaskSchema(task_model: TaskModel):
		return TaskSchema(taskId=task_model.id)
