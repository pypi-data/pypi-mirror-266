import base64
import bz2
import json
from datetime import datetime, date
from enum import Enum
from typing import Any, Type, Union, Literal
from typing import List

from pydantic import validator, root_validator, model_validator, field_validator, Field

from switcore.pydantic_base_model import SwitBaseModel
from switcore.ui.button import Button
from switcore.ui.collection_entry import CollectionEntry
from switcore.ui.container import Container
from switcore.ui.datepicker import DatePicker
from switcore.ui.divider import Divider
from switcore.ui.file import File
from switcore.ui.header import Header, AttachmentHeader
from switcore.ui.html_frame import HtmlFrame
from switcore.ui.image import Image
from switcore.ui.image_grid import ImageGrid
from switcore.ui.info_card import InfoCard
from switcore.ui.input import Input
from switcore.ui.interactive_image import InteractiveImage
from switcore.ui.select import Select, Option, OptionGroup, NoOptionsReason
from switcore.ui.signIn_page import SignInPage
from switcore.ui.tabs import Tabs
from switcore.ui.text_paragraph import TextParagraph
from switcore.ui.textarea import Textarea


class UserInfo(SwitBaseModel):
    user_id: str
    organization_id: str


class UserPreferences(SwitBaseModel):
    language: str
    time_zone_offset: str
    color_theme: str


class Settings(SwitBaseModel):
    presence_sync: bool


class MessageResource(SwitBaseModel):
    resource_type: Literal['message'] = 'message'
    id: str
    created_at: datetime
    edited_at: datetime | None = None
    content: str
    content_formatted: dict | None = None
    attachments: list[dict] | None = None
    files: list[dict] | None = None
    creator: dict

    @field_validator('edited_at', mode='before')  # noqa
    @classmethod
    def parse_empty_string_to_none(cls, v):
        if v == '':
            return None
        return v


class MessageCommentResource(MessageResource):
    resource_type: Literal['message_comment'] = 'message_comment'


class TaskStatusType(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class TaskPeriod(SwitBaseModel):
    start_time: datetime | date | None = None
    due_time: datetime | date | None = None
    include_time: bool

    @model_validator(mode='before')
    def parse_empty_strings(cls, values: dict[str, Any]):
        for field, value in values.items():
            if isinstance(value, str) and value == "":
                values[field] = None
        return values


class TaskUser(SwitBaseModel):
    id: str


class TaskStatus(SwitBaseModel):
    id: str
    name: str
    type: TaskStatusType


class TaskBucket(SwitBaseModel):
    id: str


class TaskResource(SwitBaseModel):
    resource_type: Literal['task'] = 'task'
    id: str
    parent_task_id: str | None = None
    created_at: datetime
    edited_at: datetime | None = None
    title: str
    period: TaskPeriod
    priority: Literal['highest', 'high', 'normal', 'low', 'lowest']
    color_label: Literal[
                     'red', 'pink', 'orange', 'yellow', 'light_green', 'green', 'cyan', 'blue', 'navy', 'violet', 'gray'] | None = None
    assignees: List[TaskUser]
    collaborators: List[TaskUser]
    status: TaskStatus
    bucket: TaskBucket

    @model_validator(mode='before')
    def parse_empty_strings(cls, values: dict[str, Any]):
        for field, value in values.items():
            if isinstance(value, str) and value == "":
                values[field] = None
        return values


class SettingsResource(SwitBaseModel):
    resource_type: Literal['settings.presence_sync'] = 'settings.presence_sync'
    settings: Settings


class QueryResource(SwitBaseModel):
    resource_type: Literal['query'] = 'query'
    value: str


class UserActionType(str, Enum):
    right_panel_open = "right_panel_open"
    presence_sync = "presence_sync"
    user_commands_chat = "user_commands.extensions:chat"
    user_commands_chat_extension = "user_commands.chat_extension"
    user_commands_chat_commenting = "user_commands.extensions:chat_commenting"
    user_commands_context_menus_message = "user_commands.context_menus:message"
    user_commands_context_menus_message_comment = "user_commands.context_menus:message_comment"
    view_actions_drop = "view_actions.drop"
    view_actions_input = "view_actions.input"
    view_actions_query = "view_actions.query"
    view_actions_submit = "view_actions.submit"
    view_actions_oauth_complete = "view_actions.oauth_complete"
    user_commands_context_menus_task = "user_commands.context_menus:task"  # this action has a dict resource
    user_commands_task_extension = "user_commands.extensions:task"


class UserAction(SwitBaseModel):
    type: UserActionType
    id: str
    slash_command: str
    resource: MessageResource | MessageCommentResource | SettingsResource | QueryResource | TaskResource | None = Field(
        default=None, discriminator='resource_type')
    value: str | None = None


class Context(SwitBaseModel):
    workspace_id: str | None = None
    channel_id: str | None = None
    project_id: str | None = None
    task_id: str | None = None


ElementType = (CollectionEntry | Button | Divider | File | HtmlFrame | Input | Select
               | SignInPage | TextParagraph | Image | Textarea | Container | Tabs | DatePicker | InfoCard
               | ImageGrid | InteractiveImage)

ElementTypeTuple = (CollectionEntry, Button, Divider, File, HtmlFrame, Input, Select,
                    SignInPage, TextParagraph, Image, Textarea, Container, Tabs, DatePicker, InfoCard,
                    ImageGrid, InteractiveImage)

AttachmentElementType = (CollectionEntry | InfoCard | Image | Divider | File | TextParagraph)


def contain_only_dict(elements_data: list[Union[dict, ElementType]]) -> bool:
    """
        if Body is initialized from swit_request, elements_data is list of dict
    """
    for element_data in elements_data:
        if isinstance(element_data, ElementTypeTuple):
            return False

    return True


def get_element_type(element_data: dict) -> Type[ElementType]:
    element_type_str = element_data.get('type')
    if element_type_str == 'collection_entry':
        return CollectionEntry
    elif element_type_str == 'button':
        return Button
    elif element_type_str == 'divider':
        return Divider
    elif element_type_str == 'file':
        return File
    elif element_type_str == 'html_frame':
        return HtmlFrame
    elif element_type_str == 'text_input':
        return Input
    elif element_type_str == 'select':
        return Select
    elif element_type_str == 'sign_in_page':
        return SignInPage
    elif element_type_str == 'text':
        return TextParagraph
    elif element_type_str == 'textarea':
        return Textarea
    elif element_type_str == 'image':
        return Image
    elif element_type_str == 'container':
        return Container
    elif element_type_str == 'tabs':
        return Tabs
    elif element_type_str == 'datepicker':
        return DatePicker
    elif element_type_str == 'info_card':
        return InfoCard
    elif element_type_str == 'image_grid':
        return ImageGrid
    elif element_type_str == 'interactive_image':
        return InteractiveImage
    else:
        raise ValueError(f"Unknown element type: {element_type_str}")


# class ElementMixin:
#     def __init__(self, **data: Any) -> None:
#         elements_data: list[dict | ElementType] = data.get('elements', [])
#
#         if contain_only_dict(elements_data):
#             _elements: List[ElementType] = []
#             for element_data in elements_data:
#                 assert isinstance(element_data, dict), "element_data must be dict"
#                 element_type = get_element_type(element_data)
#                 element: ElementType = element_type(**element_data)
#                 _elements.append(element)
#             data['elements'] = _elements
#
#         super().__init__(**data)  # type: ignore
#
#     def get_element_by_action_id(self, action_id: str) -> ElementType:
#         """
#         Get element by action_id if it exists, otherwise raise ValueError
#         """
#         elements: list[ElementType] = getattr(self, 'elements', [])
#         for element in elements:  # type: ignore
#             if getattr(element, 'action_id', None) is None:
#                 continue
#
#             if element.action_id == action_id:  # type: ignore
#                 return element
#
#         raise ValueError(f"Element with action_id: {action_id} not found")


class AttachmentBody(SwitBaseModel):
    elements: list[ElementType] = Field(default_factory=list, discriminator='type')


class Body(SwitBaseModel):
    elements: list[ElementType] = Field(default_factory=list, discriminator='type')


class Footer(SwitBaseModel):
    buttons: list[Button]


class ViewCallbackType(str, Enum):
    update = "views.update"
    initialize = "views.initialize"
    open = "views.open"
    push = "views.push"
    close = "views.close"


class AttachmentCallbackTypes(str, Enum):
    share_channel = "attachments.share.channel"
    share_new_task = "attachments.share.new_task"
    share_existing_task = "attachments.share.existing_task"


class SettingsCallbackTypes(str, Enum):
    settings_update = "settings.update"


class BotCallbackTypes(str, Enum):
    invite_prompt = "bot.invite_prompt"


class SuggestionsCallbackTypes(str, Enum):
    query_suggestions = "query.suggestions"


class SettingsResult(SwitBaseModel):
    success: bool = True
    error_message: str | None = None


class SuggestionsResult(SwitBaseModel):
    options: list[Option] | None = Field(default=None, max_length=50)
    option_groups: list[OptionGroup] | None = Field(default=None, max_length=10)
    no_options_reason: NoOptionsReason | None = None

    @model_validator(mode='before')
    @classmethod
    def check_suggestions_result(cls, values):
        options = values.get('options')
        option_groups = values.get('option_groups')
        no_suggestions_reason = values.get('no_suggestions_reason')

        if options:
            if option_groups or no_suggestions_reason:
                raise ValueError('If options are set, option_groups and no_suggestions_reason should not be set')

        if option_groups:
            if options or no_suggestions_reason:
                raise ValueError('If option_groups are set, options and no_suggestions_reason should not be set')

        if no_suggestions_reason:
            if options or option_groups:
                raise ValueError('If no_suggestions_reason is set, options and option_groups should not be set')

        return values

    # @field_validator('options', mode='before')  # ignore
    # @classmethod
    # def validate_options_length(cls, v):
    #     if len(v) > 50:
    #         raise ValueError("options length should be less than 50")
    #     return v
    #
    # @field_validator('option_groups', mode='before')
    # @classmethod
    # def validate_option_groups_length(cls, v):
    #     if len(v) > 10:
    #         raise ValueError("option_groups length should be less than 10")
    #     return v


class DestinationTypes(str, Enum):
    channel = 'channel'
    project = 'project'


class Destination(SwitBaseModel):
    type: DestinationTypes
    id: str


class AttachmentDestinationHint(SwitBaseModel):
    workspace_id: str | None = None
    channel_id: str | None = None
    project_id: str | None = None
    task_id: str | None = None


class AttachmentView(SwitBaseModel):
    view_id: str
    state: str | bytes
    header: AttachmentHeader
    footer: Footer | None = None
    body: AttachmentBody


class View(SwitBaseModel):
    view_id: str
    state: str | bytes
    header: Header
    footer: Footer | None = None
    body: Body


class PlatformTypes(str, Enum):
    DESKTOP = 'Desktop'
    IOS = 'iOS'
    ANDROID = 'Android'


class SwitRequest(SwitBaseModel):
    platform: PlatformTypes
    time: datetime
    app_id: str
    user_info: UserInfo
    user_preferences: UserPreferences
    context: Context
    user_action: UserAction
    current_view: View | AttachmentView | None = None

    @field_validator('current_view', mode='before')
    @classmethod
    def empty_dict_to_null(cls, v):
        if v == {}:
            return None
        return v


class SwitResponse(SwitBaseModel):
    callback_type: (ViewCallbackType | AttachmentCallbackTypes | SettingsCallbackTypes
                    | BotCallbackTypes | SuggestionsCallbackTypes)
    new_view: View | None = None
    attachments: list[AttachmentView] | None = None
    destination_hint: AttachmentDestinationHint | None = None
    reference_view_id: str | None = None
    result: SettingsResult | SuggestionsResult | None = None
    destination: Destination | None = None


class BaseState(SwitBaseModel):
    autoincrement_id: int = 1

    @classmethod
    def from_bytes(cls, byte: bytes):
        d = json.loads(bz2.decompress(base64.b64decode(byte)).decode("utf-8"))
        return cls(**d)

    def to_bytes(self) -> bytes:
        return base64.b64encode(bz2.compress(self.json().encode("utf-8"), 1))
