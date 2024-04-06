from dataclasses import dataclass

from pkgs.argument_parser import CachedParser
from uncountable.integration.construct_client import construct_uncountable_client
from uncountable.integration.executors.script_executor import resolve_script_executor
from uncountable.integration.job import CronJobArguments
from uncountable.integration.types import JobDefinition, ProfileMetadata


@dataclass
class CronJobArgs:
    definition: JobDefinition
    profile_metadata: ProfileMetadata


cron_args_parser = CachedParser(CronJobArgs)


def cron_job_executor(**kwargs: dict) -> None:
    args_passed = cron_args_parser.parse_storage(kwargs)
    args = CronJobArguments(
        job_definition=args_passed.definition,
        client=construct_uncountable_client(profile_meta=args_passed.profile_metadata),
    )

    job_class = resolve_script_executor(args_passed.definition.executor)

    job = job_class()
    job.run(args)
