import datetime
import os
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from pydantic import BaseModel
from starlette.responses import Response

from switcore.auth.exception import InvalidOauthStateException
from switcore.auth.schemas import SwitToken


class OAuth2(BaseModel):
    client_id: str
    client_secret: str
    base_url: str
    authorize_endpoint: str
    access_token_endpoint: str
    refresh_token_endpoint: str
    bot_redirect_url: str
    user_redirect_url: str
    request_headers: dict[str, str] = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    def get_bot_authorization_url(self, state: str | None = None) -> str:
        bot_scopes_or_null: str | None = os.getenv("BOT_SCOPES", None)

        scope = "app:install"
        if bot_scopes_or_null is not None:
            scope = scope + "+" + bot_scopes_or_null

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": scope,
            "redirect_uri": self.base_url + self.bot_redirect_url,
        }

        if state is not None:
            params["state"] = state

        return f"{self.authorize_endpoint}?{urlencode(params)}"

    def get_user_authorization_url(self, scope: str, state: str | None = None) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": scope,
            "redirect_uri": self.base_url + self.user_redirect_url,
        }

        if state is not None:
            params["state"] = state

        return f"{self.authorize_endpoint}?{urlencode(params)}"

    async def get_authorization_url(
            self,
            redirect_uri: str,
            scope: str,
            state: str | None = None,
            **extras_params,
    ) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
        }

        if state is not None:
            params["state"] = state

        if extras_params is not None:
            params = {**params, **extras_params}

        return f"{self.authorize_endpoint}?{urlencode(params)}"

    async def get_access_token(self, code: str, redirect_uri: str) -> SwitToken:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = await client.post(
                self.access_token_endpoint,
                data=data,
                headers=self.request_headers,
            )

            result: dict[str, Any] = response.json()

            if response.status_code >= 400:
                raise ValueError(result)

            return SwitToken(**result)

    async def refresh_token(self, refresh_token: str) -> SwitToken:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.refresh_token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                },
                headers=self.request_headers,
            )

            data: dict[str, Any] = response.json()

            if response.status_code >= 400:
                raise ValueError(data)

            return SwitToken(**data)

    async def get_secure_authorization_url(
            self,
            redirect_uri: str,
            scope: str,
            callback_payload: dict | None = None,
            **extras_params) -> str:

        if callback_payload is None:
            callback_payload = {}

        callback_payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

        swit_singing_key: str | None = os.getenv('SWIT_SINGING_KEY', None)

        assert swit_singing_key is not None, "SWIT_SINGING_KEY is not set check .env file"

        encoded_jwt = jwt.encode(callback_payload, swit_singing_key, algorithm="HS256")

        return await self.get_authorization_url(redirect_uri, scope, encoded_jwt, **extras_params)


class OAuth2AuthorizeCallbackABC(ABC):
    def __init__(self, client: OAuth2, redirect_url: str) -> None:
        self.client = client
        self.redirect_url = redirect_url

    @abstractmethod
    async def process_access_token(self, access_token: SwitToken, state: str | None) -> Response:
        pass

    async def _get_access_token(self, code: str) -> SwitToken:
        return await self.client.get_access_token(code, self.redirect_url)

    async def __call__(
            self,
            code: str,
            state: str | None,
            error: str | None = None,
    ) -> Response:
        access_token = await self._get_access_token(code)
        return await self.process_access_token(access_token, state)


class SecureOAuth2AuthorizeCallbackABC(ABC):
    def __init__(self, client: OAuth2, redirect_url: str) -> None:
        self.client = client
        self.redirect_url = redirect_url

    @abstractmethod
    async def process_access_token(self, access_token: SwitToken, callback_payload: dict) -> Response:
        pass

    async def _get_access_token(self, code: str) -> SwitToken:
        return await self.client.get_access_token(code, self.redirect_url)

    async def __call__(
            self,
            code: str,
            state: str,
            error: str | None = None,
    ) -> Response:
        swit_singing_key: str | None = os.getenv('SWIT_SINGING_KEY', None)

        assert swit_singing_key is not None, "SWIT_SINGING_KEY is not set check .env file"

        try:
            callback_payload = jwt.decode(state, swit_singing_key, algorithms=["HS256"])
        except Exception as e:
            raise InvalidOauthStateException(str(e))

        access_token = await self._get_access_token(code)
        return await self.process_access_token(access_token, callback_payload)
