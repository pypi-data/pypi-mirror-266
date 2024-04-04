import os

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse

from switcore.auth.dependencies import get_oauth
from switcore.auth.oauth2 import OAuth2

router = APIRouter()


@router.get("/bot")
async def bot_authorization(
        request: Request,  # noqa: F841
        oauth: OAuth2 = Depends(get_oauth)
):
    return RedirectResponse(
        oauth.get_bot_authorization_url(),
        status.HTTP_307_TEMPORARY_REDIRECT
    )


@router.get("/user")
async def user_authorization(
        request: Request,  # noqa: F841
        oauth: OAuth2 = Depends(get_oauth)
):
    scopes: str | None = os.getenv('SCOPES', None)

    assert scopes is not None, "SCOPES is not set check .env file"

    return RedirectResponse(
        oauth.get_user_authorization_url(scopes),
        status.HTTP_307_TEMPORARY_REDIRECT
    )


"""
in order to add callback router url to your app you need to add this snippet to your app.py file

class BotAuthorizeCallback(OAuth2AuthorizeCallbackABC):
    async def process_access_token(_self, access_token: SwitToken, state: str | None) -> http_response:  # noqa

        self.assertEqual(access_token.access_token, expected["access_token"])
        self.assertEqual(access_token.expires_in, expected["expires_in"])
        self.assertEqual(access_token.refresh_token, expected["refresh_token"])
        self.assertEqual(access_token.scope, expected["scope"])
        self.assertEqual(access_token.token_type, expected["token_type"])

        return HTMLResponse(content="<script>window.close()</script>", status_code=status.HTTP_200_OK)


@self.app.get("/auth/callback/bot")
async def bot_oauth_callback(
        request: Request,
        code: str,
        state: str,
        oauth: OAuth2 = Depends(get_oauth)
):
    callback = BotAuthorizeCallback(
        client=oauth,
        redirect_url="test_base_url/auth/callback/bot",
    )

    return await callback(
        code=code,
        state=state,
    )
"""
