import os
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse, parse_qs

from fastapi import Depends
from httpx import Response
from starlette import status
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse, HTMLResponse, RedirectResponse
from starlette.testclient import TestClient

from switcore.auth.dependencies import get_oauth
from switcore.auth.oauth2 import OAuth2AuthorizeCallbackABC, OAuth2, SecureOAuth2AuthorizeCallbackABC
from switcore.auth.router import router as auth_router
from switcore.auth.schemas import SwitToken
from tests.utils import create_fastapi_app


class OAuth2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_fastapi_app()
        self.app.include_router(auth_router, prefix="/auth")
        self.client = TestClient(self.app)
        super().setUp()

    def test_bot_authorization_url(self):
        response: Response = self.client.get("/auth/bot", follow_redirects=False)
        expected_url: str = "https://openapi.swit.io/oauth/authorize?" \
                            "response_type=code" \
                            "&client_id=test_client_id" \
                            "&scope=app:install" \
                            "&redirect_uri=test_base_url/auth/callback/bot"
        decoded_url: str = unquote(response.headers["location"])
        self.assertEqual(expected_url, decoded_url)

    def test_oauth2_callback_handler(self):
        expected = {
            "access_token": "eyJhbGciOiJIUzUxMiIsInR5cxxxxxxx.xxxxxxxx.xxxxxxxxxx",
            "expires_in": 604800,
            "refresh_token": "QIDQFWZZXFCXXXXX_XXXXX",
            "scope": "app:install",
            "token_type": "Bearer"
        }

        class BotAuthorizeCallback(OAuth2AuthorizeCallbackABC):
            async def process_access_token(
                    _self,  # noqa F841
                    swit_token: SwitToken,
                    state: str | None
            ) -> StarletteResponse:
                self.assertEqual(swit_token.access_token, expected["access_token"])
                self.assertEqual(swit_token.expires_in, expected["expires_in"])
                self.assertEqual(swit_token.refresh_token, expected["refresh_token"])
                self.assertEqual(swit_token.scope, expected["scope"])
                self.assertEqual(swit_token.token_type, expected["token_type"])
                return HTMLResponse(content="<script>window.close()</script>", status_code=status.HTTP_200_OK)

        @self.app.get("/auth/callback/bot")
        async def bot_oauth_callback(
                request: Request,  # noqa F841
                code: str,
                state: str | None = None,
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

        with patch('httpx.AsyncClient.post', return_value=Response(200, json=expected)) as mock_post:
            response = self.client.get("/auth/callback/bot?code=test_code&state=test_state")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.content, b"<script>window.close()</script>")
            mock_post.assert_called_once()

    def test_oauth2_secure_state(self):
        expected = {
            "access_token": "eyJhbGciOiJIUzUxMiIsInR5cxxxxxxx.xxxxxxxx.xxxxxxxxxx",
            "expires_in": 604800,
            "refresh_token": "QIDQFWZZXFCXXXXX_XXXXX",
            "scope": "app:install",
            "token_type": "Bearer"
        }

        pass_callback_payload = {
            "user_id": "el.lee@swit.io",
            "workspace": "swit_group",
        }

        class SecureAuthorizeCallback(SecureOAuth2AuthorizeCallbackABC):
            async def process_access_token(
                    _self,  # noqa F841
                    swit_token: SwitToken,
                    callback_payload: dict) -> StarletteResponse:
                self.assertEqual(pass_callback_payload["user_id"], callback_payload["user_id"])
                self.assertEqual(pass_callback_payload["workspace"], callback_payload["workspace"])
                self.assertEqual(swit_token.access_token, expected["access_token"])
                self.assertEqual(swit_token.expires_in, expected["expires_in"])
                self.assertEqual(swit_token.refresh_token, expected["refresh_token"])
                self.assertEqual(swit_token.scope, expected["scope"])
                self.assertEqual(swit_token.token_type, expected["token_type"])
                return HTMLResponse(content="<script>window.close()</script>", status_code=status.HTTP_200_OK)

        @self.app.get("/auth/callback/secure-user")
        async def user_oauth_callback(
                request: Request,  # noqa F841
                code: str,
                state: str | None = None,
                oauth: OAuth2 = Depends(get_oauth)
        ):
            callback = SecureAuthorizeCallback(
                client=oauth,
                redirect_url="test_base_url/auth/callback/user",
            )

            return await callback(
                code=code,
                state=state,  # type: ignore
            )

        @self.app.get("/auth/secure-user")
        async def user_authorization(
                request: Request,  # noqa: F841
                oauth: OAuth2 = Depends(get_oauth)
        ):
            scope: str | None = os.getenv('SCOPES', None)

            assert scope is not None, "SCOPES is not set check .env file"

            url: str = await oauth.get_secure_authorization_url(
                redirect_uri=oauth.base_url + "/auth/callback/user",
                scope=scope,
                callback_payload=pass_callback_payload
            )

            return RedirectResponse(
                url,
                status.HTTP_307_TEMPORARY_REDIRECT
            )

        response: Response = self.client.get("/auth/secure-user", follow_redirects=False)

        self.assertEqual(response.status_code, status.HTTP_307_TEMPORARY_REDIRECT)

        parsed_url = urlparse(response.headers.get("Location"))
        query_params = parse_qs(parsed_url.query)

        self.assertEqual(len(query_params['state']), 1)
        jwt_state: str = query_params['state'][0]

        with patch('httpx.AsyncClient.post', return_value=Response(200, json=expected)) as mock_post:
            response = self.client.get(f"/auth/callback/secure-user?code=test_code&state={jwt_state}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.content, b"<script>window.close()</script>")
            mock_post.assert_called_once()
