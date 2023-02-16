from services.models import Service
from stats.models import StatsBase, ServiceStats, StatusCount
from tasks.models import TaskStatus
from logger.logger import Logger, get_logger
from fastapi import Depends
from sqlmodel import Session, func
from database import get_session
from tasks.models import Task


class StatsService:
    def __init__(self, logger: Logger = Depends(get_logger),
                 session: Session = Depends(get_session)):
        self.logger = logger
        self.logger.set_source(__name__)
        self.session = session

    def stats(self):
        """
        Get stats about the current state of the engine
        :return: StatsBase object containing stats about the current state of the engine
        """

        stats = StatsBase(summary=[], services=[])

        # Get Tasks count per service
        task_service_count = self.session.query(Task.service_id, func.count(Task.id)).group_by(Task.service_id).all()

        # Get all services with their tasks and count the number of tasks per status
        task_status_count = self.session.query(
            Service.id, Service.name, Task.status, func.count(Task.status)
        ).join(
            Service
        ).where(
            Service.id == Task.service_id
        ).group_by(
            Task.status, Task.service_id
        ).all()

        # Get the total number of tasks per status keep empty status with 0
        total_status_count = self.session.query(Task.status, func.count(Task.status)).group_by(Task.status).all()

        # Add the stats fot the services to the StatsBase object
        stats.services = [ServiceStats(service_id=service_stats[0],
                                       service_name=service_stats[1],
                                       total=next((service_count[1] for service_count in task_service_count if
                                                   service_count[0] == service_stats[0]), 0),
                                       status=[StatusCount(status=service_stats[2], count=service_stats[3])]
                                       ) for service_stats in task_status_count]
        # Append empty status with 0
        for service_stats in stats.services:
            for status in TaskStatus:
                if status not in [status_count.status for status_count in service_stats.status]:
                    service_stats.status.append(StatusCount(status=status, count=0))

        # Add the stats for the total number of tasks to the StatsBase object
        stats.summary = [StatusCount(status=status[0], count=status[1]) for status in total_status_count]
        # Append empty status with 0
        for status in TaskStatus:
            if status not in [status_count.status for status_count in stats.summary]:
                stats.summary.append(StatusCount(status=status, count=0))

        return stats
