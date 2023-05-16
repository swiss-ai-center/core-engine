from fastapi import Depends
from sqlmodel import Session, select, desc
from database import get_session
from common_code.logger.logger import Logger, get_logger
from uuid import UUID
from http_client import HttpClient
from tasks.models import Task, TaskUpdate
from common.exceptions import NotFoundException


class TasksService:
    def __init__(
            self,
            logger: Logger = Depends(get_logger),
            session: Session = Depends(get_session),
            http_client: HttpClient = Depends(),
    ):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session
        self.http_client = http_client

    def find_many(self, skip: int = 0, limit: int = 100):
        self.logger.debug("Find many tasks")
        return self.session.exec(select(Task).order_by(desc(Task.created_at)).offset(skip).limit(limit)).all()

    def create(self, task: Task):
        self.logger.debug("Creating task")

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        self.logger.debug(f"Created task with id {task.id}")

        return task

    def find_one(self, task_id: UUID):
        self.logger.debug("Find task")

        return self.session.get(Task, task_id)

    async def get_status_from_service(self, task: Task):
        self.logger.debug("Get task status from service")
        status = await self.http_client.get(f"{task.service.url}/tasks/{task.id}/status")
        self.logger.debug(f"Got status {status} from service {task.service.url}")
        task.status = status

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def update(self, task_id: UUID, task: TaskUpdate):
        self.logger.debug("Update task")
        current_task = self.session.get(Task, task_id)
        if not current_task:
            raise NotFoundException("Task Not Found")
        task_data = task.dict(exclude_unset=True)
        self.logger.debug(f"Updating task {task_id} with data: {task_data}")
        setattr(current_task, "status", task_data["status"])
        setattr(current_task, "data_out", task_data["data_out"])
        self.session.add(current_task)
        self.session.commit()
        self.session.refresh(current_task)
        self.logger.debug(f"Updated task with id {current_task.id}")
        return current_task

    def delete(self, task_id: UUID):
        self.logger.debug("Delete task")
        current_task = self.session.get(Task, task_id)
        if not current_task:
            raise NotFoundException("Task Not Found")
        self.session.delete(current_task)
        self.session.commit()
        self.logger.debug(f"Deleted task with id {current_task.id}")
