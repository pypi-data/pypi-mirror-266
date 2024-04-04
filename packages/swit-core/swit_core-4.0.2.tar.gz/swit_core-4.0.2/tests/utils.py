import datetime
import os

from fastapi import FastAPI

from switcore.action.async_activity_handler_abc import AsyncActivityHandlerABC
from switcore.action.schemas import SwitRequest, PlatformTypes, UserInfo, UserPreferences, Context, UserAction, \
    UserActionType, View, Body, BaseState, SwitResponse
from switcore.ui.header import Header


def create_fastapi_app():
    os.environ["SWIT_CLIENT_ID"] = "test_client_id"
    os.environ["SWIT_CLIENT_SECRET"] = "test_client_secret"
    os.environ["SWIT_SINGING_KEY"] = "test_singing_key"
    os.environ["APPS_ID"] = "test_apps_id"
    os.environ["DB_USERNAME"] = "test_db_username"
    os.environ["DB_PASSWORD"] = "test_db_password"
    os.environ["DB_NAME"] = "test_db_name"
    os.environ["ENV_OPERATION"] = "local"
    os.environ["BASE_URL"] = "test_base_url"
    os.environ["LOCALIZE_PROJECT_ID"] = "test_localize_project_id"
    os.environ["DB_HOST"] = "test_db_host"
    os.environ[
        "SCOPES"] = ("imap:write+imap:read+user:read+message:write+channel:read+workspace:read+project"
                     ":read+project:write+task:read+task:write")
    os.environ["BOT_REDIRECT_URL"] = "/auth/callback/bot"
    os.environ["USER_REDIRECT_URL"] = "/auth/callback/user"

    return FastAPI()


class ActivityHandler(AsyncActivityHandlerABC):

    def on_user_commands_task_extension(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    def on_user_commands_context_menus_task(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_query(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, query: str, *args, **kwargs) -> SwitResponse:
        pass

    async def on_right_panel_open(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_presence_sync(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat_extension(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat_commenting(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_context_menus_message(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_context_menus_message_comment(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_view_actions_drop(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_view_actions_oauth_complete(  # type: ignore
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass


def create_submit_swit_request(view_id: str, action_id: str):
    return SwitRequest(
        platform=PlatformTypes.DESKTOP,
        time=datetime.datetime.now(),
        app_id="test_app_id",
        user_info=UserInfo(
            user_id="test_user_id",
            organization_id="test_organization_id"
        ),
        user_preferences=UserPreferences(
            language="ko",
            time_zone_offset="+0900",
            color_theme="light"
        ),
        context=Context(
            workspace_id="test_workspace_id",
            channel_id="test_channel_id"
        ),
        user_action=UserAction(
            type=UserActionType.view_actions_submit,
            id=action_id,
            slash_command="test_slash_command",
        ),
        current_view=View(
            view_id=view_id,
            state="state",
            header=Header(
                title="test_title",
            ),
            body=Body(
                elements=[]
            ),
        ))


def create_query_swit_request():
    _json = {'time': '2023-12-27T06:12:22.498Z', 'app_id': '230824012947339SP3AX', 'platform': 'Desktop',
             'context': {'workspace_id': '', 'channel_id': '', 'project_id': '', 'task_id': '', 'message': None,
                         'task': None, 'approval_request_id': ''},
             'user_action': {'type': 'view_actions.query', 'id': 'example14_server_query', 'slash_command': '',
                             'resource': {'resource_type': 'query', 'value': 'q'}},
             'user_preferences': {'language': 'en', 'time_zone_offset': '+0900', 'color_theme': 'light'},
             'user_info': {'user_id': '23042402102425L72QG7', 'organization_id': '2209220405404NAp2M9'}}

    return SwitRequest(**_json)


def create_task_swit_request(period: dict | None = None):
    _json = {
        'time': '2023-12-27T06:12:22.498Z',
        'app_id': '230824012947339SP3AX',
        'platform': 'Desktop',
        'context': {'workspace_id': '', 'channel_id': '', 'project_id': '', 'task_id': '', 'message': None,
                    'task': None, 'approval_request_id': ''},
        'user_action': {
            'type': 'user_commands.context_menus:task',
            'id': 'example14_server_query', 'slash_command': '',
            'resource': {
                "resource_type": "task",
                "id": "23051106260551ZOVCPS",
                "parent_task_id": "200302045745598izpK",
                "created_at": "2022-07-07T12:41:18Z",
                "edited_at": "2022-07-08T07:22:18Z",
                "title": "Developers documentation",
                "period": {
                    "start_time": "",
                    "due_time": "2023-02-14T05:01:00.452591Z",
                    "include_time": True
                } if period is None else period,
                "priority": "highest",
                "color_label": "",
                "assignees": [
                    {
                        "id": "220103011810x7bqTRZ"
                    }
                ],
                "collaborators": [
                    {
                        "id": "220103011810x7bqTRZ"
                    }
                ],
                "status": {
                    "id": "220707214090V110qhk",
                    "name": "Done",
                    "type": "not_started"
                },
                "bucket": {
                    "id": "230213021820Zc9NjbT"
                }
            }},
        'user_preferences': {'language': 'en', 'time_zone_offset': '+0900', 'color_theme': 'light'},
        'user_info': {'user_id': '23042402102425L72QG7', 'organization_id': '2209220405404NAp2M9'}
    }

    return SwitRequest(**_json)
