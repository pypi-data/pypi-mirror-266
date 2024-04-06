

import importlib
import inspect
from uncountable.integration.job import Job
from uncountable.integration.types import JobExecutorScript


def resolve_script_executor(executor: JobExecutorScript) -> type[Job]:
    job_module = importlib.import_module(executor.import_path)
    found_jobs: list[type[Job]] = []
    for _, job_class in inspect.getmembers(job_module, inspect.isclass):
        if Job in job_class.__bases__:
            found_jobs.append(job_class())
    assert (
        len(found_jobs) == 1
    ), f"expected exactly one job class in {executor.import_path}"
    return found_jobs[0]
