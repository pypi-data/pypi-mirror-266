import os
from typing import assert_never

from uncountable.core.client import AuthDetailsApiKey, Client
from uncountable.integration.types import (
    AuthRetrievalEnv,
    ProfileMetadata,
)


def _get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise Exception(f"environment variable {name} is missing")
    return value


def construct_uncountable_client(profile_meta: ProfileMetadata) -> Client:
    match profile_meta.auth_retrieval:
        case AuthRetrievalEnv():
            api_id = _get_env_var(f"UNC_PROFILE_{profile_meta.name.upper()}_API_ID")
            api_secret_key = _get_env_var(
                f"UNC_PROFILE_{profile_meta.name.upper()}_API_SECRET_KEY"
            )

            assert api_id is not None
            assert api_secret_key is not None

            return Client(
                base_url=profile_meta.base_url,
                auth_details=AuthDetailsApiKey(
                    api_id=api_id, api_secret_key=api_secret_key
                ),
            )
    assert_never(profile_meta.auth_retrieval)
