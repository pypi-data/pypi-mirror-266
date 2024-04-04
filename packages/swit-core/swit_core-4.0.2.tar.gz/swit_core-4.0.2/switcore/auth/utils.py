import os

from switcore.constants import Environment


def get_swit_openapi_base_url() -> str:
    env: str | None = os.getenv('ENV_OPERATION', None)

    assert env is not None, "ENV_OPERATION is not set check .env file"

    if env == Environment.LOCAL or env == Environment.PROD:
        return 'https://openapi.swit.io'
    elif env == Environment.EXPRESS:
        return 'https://openapi.swit.express'
    elif env == Environment.DEV:
        return 'https://openapi2.swit.dev'
    else:
        raise ValueError(f"Invalid ENV_OPERATION: {env}")
