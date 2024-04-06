import os
from importlib import resources

from uncountable.integration.server import IntegrationServer
from uncountable.integration.types import ProfileDefinition
from pkgs.argument_parser import CachedParser
from uncountable.integration.db.connect import create_db_engine


profile_parser = CachedParser(ProfileDefinition)


def main() -> None:
    profiles_module = os.environ["UNC_PROFILES_MODULE"]
    with IntegrationServer(create_db_engine()) as server:
        # TODO: Loop through all job spec yaml files and call server.add_job
        profiles = [
            entry
            for entry in resources.files(profiles_module).iterdir()
            if entry.is_dir()
        ]
        for profile in profiles:
            profile_name = profile.name
            try:
                profile = profile_parser.parse_yaml_resource(
                    package=".".join([profiles_module, profile_name]),
                    resource="profile.yaml",
                )
            except FileNotFoundError as e:
                print("WARN: profile.yaml not found", e)
                continue
            server.register_profile(
                profile_name=profile_name,
                base_url=profile.base_url,
                auth_retrieval=profile.auth_retrieval,
                jobs=profile.jobs,
            )

        server.serve_forever()


if __name__ == "__main__":
    main()
