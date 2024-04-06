# TODO: move to type spec


from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class JobDefinitionType(StrEnum):
    CRON = "cron"
    # also imagine other job types like webhook-triggered or sftp-triggered,
    # manual, etc


class JobExecutorType(StrEnum):
    SCRIPT = "script"
    # also imagine builtin executors like 'sftp_sync'


class AuthRetrievalType(StrEnum):
    ENV = "env"
    # also imagine secrets manager, keyvault, etc


@dataclass
class JobExecutorBase:
    type: JobExecutorType


@dataclass
class JobExecutorScript(JobExecutorBase):
    type: Literal[JobExecutorType.SCRIPT]
    import_path: str


JobExecutor = JobExecutorScript


@dataclass
class JobDefinitionBase:
    id: str
    name: str


@dataclass
class CronJobDefinition(JobDefinitionBase):
    type: Literal[JobDefinitionType.CRON]
    cron_spec: str
    # Here we assert that the executor has to be a script, but we could add
    # other builtin executor types that cron jobs can support later
    executor: JobExecutorScript


JobDefinition = CronJobDefinition


@dataclass
class AuthRetrievalBase:
    type: AuthRetrievalType


@dataclass
class AuthRetrievalEnv:
    # We don't really need any extra info here, we can enforce that the auth
    # keys are named like UNC_PROFILE_{profile name}_API_SECRET_KEY. For
    # supporting pulling secrets from secrets manager etc it will be nice to
    # use dataclass properties to get the secret name, region etc.
    type: Literal[AuthRetrievalType.ENV]


AuthRetrieval = AuthRetrievalEnv


@dataclass
class ProfileDefinition:
    # profile name (expected to be something like customer_name) will be
    # obtained from the folder name instead of specified here. Forces jobs to
    # be organized nicely in folders that separate their identities.
    auth_retrieval: AuthRetrieval
    base_url: str
    jobs: list[JobDefinition]


@dataclass
class ProfileMetadata:
    # supplied by inspecting the folder name that the profile is in
    name: str
    base_url: str
    auth_retrieval: AuthRetrieval
