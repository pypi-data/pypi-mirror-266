import signal
from types import TracebackType
from dataclasses import asdict
from typing import Optional, assert_never
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from uncountable.integration.cron import CronJobArgs, cron_job_executor
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.engine.base import Engine

from uncountable.integration.types import (
    AuthRetrieval,
    CronJobDefinition,
    JobDefinition,
    ProfileMetadata,
)


_MAX_APSCHEDULER_CONCURRENT_JOBS = 1


class IntegrationServer:
    _scheduler: BaseScheduler
    _engine: Engine

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._scheduler = BackgroundScheduler(
            timezone="UTC",
            jobstores={"default": SQLAlchemyJobStore(engine=engine)},
            executors={"default": ThreadPoolExecutor(_MAX_APSCHEDULER_CONCURRENT_JOBS)},
        )

    def register_profile(
        self,
        *,
        profile_name: str,
        base_url: str,
        auth_retrieval: AuthRetrieval,
        jobs: list[JobDefinition],
    ) -> None:
        for job_defn in jobs:
            profile_metadata = ProfileMetadata(
                name=profile_name, auth_retrieval=auth_retrieval, base_url=base_url
            )
            match job_defn:
                case CronJobDefinition():
                    # Add to ap scheduler
                    job_kwargs = asdict(
                        CronJobArgs(
                            definition=job_defn, profile_metadata=profile_metadata
                        )
                    )
                    existing_job = self._scheduler.get_job(job_defn.id)
                    if existing_job is not None:
                        existing_job.modify(
                            name=job_defn.name,
                            kwargs=job_kwargs,
                        )
                        existing_job.reschedule(
                            CronTrigger.from_crontab(job_defn.cron_spec)
                        )
                    else:
                        self._scheduler.add_job(
                            cron_job_executor,
                            # IMPROVE: reconsider these defaults
                            max_instances=1,
                            coalesce=True,
                            trigger=CronTrigger.from_crontab(job_defn.cron_spec),
                            name=job_defn.name,
                            id=job_defn.id,
                            kwargs=job_kwargs,
                        )
                case _:
                    assert_never(job_defn.trigger)

    def serve_forever(self) -> None:
        signal.pause()

    def _start_apscheduler(self) -> None:
        self._scheduler.start()

    def _stop_apscheduler(self) -> None:
        self._scheduler.shutdown()

    def __enter__(self) -> "IntegrationServer":
        self._start_apscheduler()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._stop_apscheduler()
