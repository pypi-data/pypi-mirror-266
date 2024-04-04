import os

from switcore.auth.oauth2 import OAuth2
from switcore.auth.utils import get_swit_openapi_base_url


def get_oauth() -> OAuth2:
    swit_client_id: str | None = os.getenv('SWIT_CLIENT_ID', None)
    swit_client_secret: str | None = os.getenv('SWIT_CLIENT_SECRET', None)
    base_url: str | None = os.getenv('BASE_URL', None)
    bot_redirect_url: str = os.getenv('BOT_REDIRECT_URL', "/auth/callback/bot")
    user_redirect_url: str = os.getenv('USER_REDIRECT_URL', "/auth/callback/user")

    assert swit_client_id is not None, "SWIT_CLIENT_ID is not set check .env file"
    assert swit_client_secret is not None, "SWIT_CLIENT_SECRET is not set check .env file"
    assert base_url is not None, "BASE_URL is not set check .env file"

    return OAuth2(
        client_id=swit_client_id,
        client_secret=swit_client_secret,
        base_url=base_url,
        authorize_endpoint=f"{get_swit_openapi_base_url()}/oauth/authorize",
        access_token_endpoint=f"{get_swit_openapi_base_url()}/oauth/token",
        refresh_token_endpoint=f"{get_swit_openapi_base_url()}/oauth/token",
        bot_redirect_url=bot_redirect_url,
        user_redirect_url=user_redirect_url,
    )
