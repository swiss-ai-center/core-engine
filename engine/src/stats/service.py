from pipelines.models import Pipeline
from services.models import Service
from tasks.models import TaskStatus
from logger import Logger
from fastapi import Depends
from sqlmodel import Session, func, select
from database import get_session
from tasks.models import Task


class StatsService:
    def __init__(self, logger: Logger = Depends(),
                 session: Session = Depends(get_session)):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session

    def stats(self):
        running = 0
        finished = 0
        error = 0
        pending = 0
        unavailable = 0

        task_service = self.session.query(Task).all()

        services_tasks_count = dict()
        pipeline_tasks_count = dict()

        services_list = self.session.query(Service).all()
        for service in services_list:
            services_tasks_count[service.name] = 0

        pipeline_list = self.session.query(Pipeline).all()
        for pipeline in pipeline_list:
            pipeline_tasks_count[pipeline.name] = 0

        for task in task_service:
            if task.pipeline is not None:
                pipeline_tasks_count[task.pipeline.name] += 1
            else:
                services_tasks_count[task.service.name] += 1

        task_total = self.session.query(Task).count()

        task_status_count = self.session.query(Task.status, func.count(Task.status)).group_by(Task.status).all()

        for task in task_status_count:
            if task[0] == TaskStatus.RUNNING:
                running = task[1]
            elif task[0] == TaskStatus.FINISHED:
                finished = task[1]
            elif task[0] == TaskStatus.ERROR:
                error = task[1]
            elif task[0] == TaskStatus.PENDING:
                pending = task[1]
            elif task[0] == TaskStatus.UNAVAILABLE:
                unavailable = task[1]

        stats = {"tasks": {"total": task_total,
                           "running": running,
                           "finished": finished,
                           "pending": pending,
                           "error": error,
                           "unavailable": unavailable},
                 "services": services_tasks_count,
                 "pipelines": pipeline_tasks_count}

        return stats
