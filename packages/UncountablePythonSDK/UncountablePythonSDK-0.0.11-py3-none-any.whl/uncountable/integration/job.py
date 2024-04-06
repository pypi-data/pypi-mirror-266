from dataclasses import dataclass
from uncountable.core.client import Client
from uncountable.integration.types import JobDefinition

from abc import ABC, abstractmethod


@dataclass
class JobArgumentsBase:
    job_definition: JobDefinition
    client: Client


@dataclass
class CronJobArguments(JobArgumentsBase):
    # can imagine passing additional data such as in the sftp or webhook cases
    pass


JobArguments = CronJobArguments


@dataclass
class JobResult:
    success: bool


class Job(ABC):

    @abstractmethod
    def run(self, args: JobArguments) -> JobResult:
        ...


class CronJob(Job):

    @abstractmethod
    def run(self, args: CronJobArguments) -> JobResult:
        ...
