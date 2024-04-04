import os

import httpx
from httpx import Response
from sqlalchemy.orm import Session

from switcore.auth.models import User
from switcore.auth.repository import AppRepository, UserRepository
from switcore.auth.schemas import SwitToken


class CustomHTTPClient(httpx.Client):
    def __init__(self,
                 base_url: str,
                 access_token: str,
                 refresh_token: str,
                 session: Session,
                 refresh_token_url,
                 swit_id_or_null: str | None = None,
                 app_id_or_null: str | None = None,
                 cmp_id_or_null: str | None = None,
                 *args, **kwargs):

        assert (swit_id_or_null is None) ^ (app_id_or_null is None), \
            "Either swit_id or app_id should be provided, but not both."

        if swit_id_or_null:
            assert cmp_id_or_null is None, "Please input cmp_id"

        if app_id_or_null:
            assert cmp_id_or_null, "Please input cmp_id"

        kwargs['timeout'] = 3.0
        super().__init__(*args, **kwargs)
        self.base_url = base_url  # type: ignore
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.swit_id_or_null = swit_id_or_null
        self.app_id_or_null = app_id_or_null
        self.cmp_id_or_null = cmp_id_or_null
        self.refresh_token_url = refresh_token_url
        self.session = session
        self.is_user = swit_id_or_null is not None

    def add_auth_header(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def refresh(self) -> None:
        client_id: str | None = os.getenv('SWIT_CLIENT_ID', None)
        client_secret: str | None = os.getenv('SWIT_CLIENT_SECRET', None)

        assert client_id is not None, "check SWIT_CLIENT_ID in env!!"
        assert client_secret is not None, "check SWIT_CLIENT_SECRET in env!!"

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": self.refresh_token,
        }

        url = self.build_url(self.refresh_token_url)

        response = self.post(
            url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        swit_token: SwitToken = SwitToken(**response.json())
        if self.is_user:
            assert self.swit_id_or_null is not None, "swit_id should not be null"

            user: User = UserRepository(self.session).update_token(
                self.swit_id_or_null,
                swit_token.access_token,
                swit_token.refresh_token
            )
            self.access_token = user.access_token
            self.refresh_token = user.refresh_token
        else:
            assert self.cmp_id_or_null is not None, "cmp_id should not be null"
            assert self.app_id_or_null is not None, "app_id should not be null"

            app = AppRepository(self.session).update_token(
                self.cmp_id_or_null,
                self.app_id_or_null,
                swit_token.access_token,
                swit_token.refresh_token
            )
            self.access_token = app.access_token
            self.refresh_token = app.refresh_token

    def build_url(self, path):
        return f"{self.base_url}{path}"

    def api_get(self, path, **kwargs):
        url = self.build_url(path)
        return self.get(url, headers=self.add_auth_header(), **kwargs)

    def api_post(self, path, data, **kwargs):
        url = self.build_url(path)
        return self.post(url, headers=self.add_auth_header(), json=data, **kwargs)

    def is_refresh_request(self, args: tuple):
        return len(args) == 1 and args[0] == self.build_url(self.refresh_token_url)

    def request(self, method: str, *args, **kwargs) -> Response:
        if self.is_refresh_request(args):
            return super().request(method, *args, **kwargs)
        else:
            response: Response = super().request(method, *args, **kwargs)
            if response.status_code == 401:
                self.refresh()
                kwargs['headers'] = self.add_auth_header()
                response = super().request(method, *args, **kwargs)
                assert response.status_code != 401, "refresh token failed"
            return response
