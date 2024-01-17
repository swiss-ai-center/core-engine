from services.models import Service
from stats.models import StatsBase, ServiceStats, StatusCount
from tasks.models import TaskStatus
from common_code.logger.logger import Logger, get_logger
from fastapi import Depends
from sqlmodel import Session, func, select
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

        stats = StatsBase(total=0, summary=[], services=[])

        # Get all services with their tasks and count the number of tasks per status

        statement = select(
            Service.id, Service.name, Task.status, func.count(Task.status)
        ).join(
            Service
        ).where(
            Service.id == Task.service_id
        ).group_by(
            Service.id, Task.status
        )
        task_status_count = self.session.exec(statement).all()

        # Get the total number of tasks per status keep empty status with 0
        statement = select(
            Task.status, func.count(Task.status)
        ).group_by(
            Task.status
        )
        total_status_count = self.session.exec(statement).all()

        # For each service, add the status count to the ServiceStats object for each status
        for service_id, service_name, status, count in task_status_count:
            service_stats = [
                service_stats for service_stats in stats.services if service_stats.service_id == service_id
            ]
            if len(service_stats) == 0:
                service_stats = ServiceStats(service_id=service_id, service_name=service_name, total=count,
                                             status=[StatusCount(status=status, count=count)])
                stats.services.append(service_stats)
            else:
                service_stats = service_stats[0]

                service_stats.status.append(StatusCount(status=status, count=count))
                service_stats.total += count

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

        # Add the total number of tasks to the StatsBase object
        stats.total = sum([status_count.count for status_count in stats.summary])

        return stats
