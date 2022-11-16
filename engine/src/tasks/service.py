from fastapi import Depends
from storage import Storage
from sqlmodel import Session, select
from database import get_session
from logger import Logger
from .models import Task, TaskRead
from .enums import TaskStatus


class TasksService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), session: Session = Depends(get_session)):
        self.logger = logger
        self.storage = storage
        self.db = session

    def find_many(self, skip: int = 0, limit: int = 100) -> list[TaskRead] :
        self.logger.debug("Find many tasks")
        return self.db.exec(select(Task).offset(skip).limit(limit)).all()

    def create(self):
        self.logger.debug("Creating task")
        task = Task()
        task.status = TaskStatus.PENDING

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self.logger.debug(f"Created task with id {task.id}")

        return task

    def find_one(self, task_id: int) -> TaskRead:
        self.logger.debug("Find first task")
        return self.db.get(Task, task_id)

    # TODO: Implement update method
    def update(self):
        self.logger.debug("Update task")

    # TODO: Implement delete method
    def delete(self):
        self.logger.debug("Delete task")
