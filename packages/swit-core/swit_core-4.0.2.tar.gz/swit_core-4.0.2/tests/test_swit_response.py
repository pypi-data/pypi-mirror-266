import json  # noqa: F401
import unittest

from switcore.action.schemas import SwitResponse, ViewCallbackType, View, Body, AttachmentCallbackTypes, AttachmentView, \
    AttachmentBody, SuggestionsCallbackTypes, SuggestionsResult, NoOptionsReason, AttachmentDestinationHint
from switcore.ui.divider import Divider
from switcore.ui.element_components import Tag, TagStyle
from switcore.ui.header import Header, AttachmentHeader
from switcore.ui.image import Image
from switcore.ui.select import Option, OptionGroup
from switcore.ui.text_paragraph import TextParagraph


class SwitViewResponseTest(unittest.TestCase):

    def test_swit_response_view(self):
        body = Body(
            elements=[TextParagraph(content="test content"), Divider()],
        )
        swit_response = SwitResponse(
            callback_type=ViewCallbackType.update,
            new_view=View(
                view_id="test01",
                state="test state",
                header=Header(title="this is Header"),
                body=body,
            )
        )
        expected: dict = {
            'callback_type': ViewCallbackType.update,
            'new_view': {
                'view_id': 'test01',
                'state': "test state",
                'header': {'title': 'this is Header'},
                'body': {
                    'elements': [
                        {
                            'content': 'test content',
                            'markdown': False,
                            'type': 'text'
                        },
                        {
                            'type': 'divider'
                        }
                    ],
                }
            }
        }
        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_attachments(self):
        swit_response = SwitResponse(
            callback_type=AttachmentCallbackTypes.share_channel,
            attachments=[AttachmentView(
                view_id="test01",
                state="test state",
                header=AttachmentHeader(
                    title="this is Header",
                    app_id="test app id",
                    icon=Image(
                        image_url="https://example.com/image.png",
                    ),
                ),
                body=AttachmentBody(
                    elements=[TextParagraph(content="test content")],
                ),
            )],
            destination_hint=AttachmentDestinationHint(
                workspace_id="1234",
                channel_id="5678",
            )
        )
        expected: dict = {
            'callback_type': 'attachments.share.channel',
            'attachments': [{
                'view_id': 'test01',
                'state': "test state",
                'header': {
                    'title': 'this is Header',
                    'app_id': 'test app id',
                    'icon': {
                        'type': 'image',
                        'image_url': 'https://example.com/image.png'
                    }
                },
                'body': {
                    'elements': [
                        {
                            'content': 'test content',
                            'markdown': False,
                            'type': 'text'
                        }
                    ],
                }
            }],
            'destination_hint': {
                'workspace_id': '1234',
                'channel_id': '5678'
            }
        }
        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_query_suggestion01(self):
        swit_response = SwitResponse(
            callback_type=SuggestionsCallbackTypes.query_suggestions,
            result=SuggestionsResult(
                options=[Option(
                    label="Search 성공!",
                    action_id="success_option_action_id",
                )],
            )
        )

        expected: dict = {
            'callback_type': SuggestionsCallbackTypes.query_suggestions,
            'result': {
                'options': [{
                    'label': 'Search 성공!',
                    'action_id': 'success_option_action_id'
                }]
            }
        }
        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_query_suggestion02(self):
        options: list[Option] = [
            Option(
                label="test label1",
                icon=Image(
                    image_url="https://files.swit.dev/webhook_logo.png",
                ),
                tag=Tag(content="no style"),
                action_id="test_action_id1"
            ),
            Option(
                label="test label2",
                action_id="test_action_id2",
                tag=Tag(content="red rounded", style=TagStyle(color='danger', shape='rounded')),
            ),
            Option(
                label="test label3",
                icon=Image(
                    image_url="https://files.swit.dev/webhook_logo.png",
                ),
                action_id="test_action_id3",
            ),
        ]

        swit_response = SwitResponse(
            callback_type=SuggestionsCallbackTypes.query_suggestions,
            result=SuggestionsResult(
                options=options,
            )
        )

        expected: dict = {
            'callback_type': SuggestionsCallbackTypes.query_suggestions.value,
            'result': {
                'options': [
                    {
                        'label': 'test label1',
                        'icon': {
                            'type': 'image',
                            'image_url': 'https://files.swit.dev/webhook_logo.png'
                        },
                        'tag': {
                            'type': 'tag',
                            'content': 'no style'
                        },
                        'action_id': 'test_action_id1'
                    },
                    {
                        'label': 'test label2',
                        'tag': {
                            'type': 'tag',
                            'content': 'red rounded',
                            'style': {
                                'color': 'danger',
                                'shape': 'rounded'
                            }
                        },
                        'action_id': 'test_action_id2'
                    },
                    {
                        'label': 'test label3',
                        'icon': {
                            'type': 'image',
                            'image_url': 'https://files.swit.dev/webhook_logo.png'
                        },
                        'action_id': 'test_action_id3'
                    }
                ]
            }
        }

        # convert expected json to json format
        expected_json = json.dumps(expected)

        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_query_suggestions03(self):
        with self.assertRaises(ValueError):
            SwitResponse(
                callback_type=SuggestionsCallbackTypes.query_suggestions,
                result=SuggestionsResult(
                    options=[Option(
                        label="Search 성공!",
                        action_id="success_option_action_id",
                    )],
                    option_groups=[
                        OptionGroup(
                            label="test group",
                            options=[Option(
                                label="test label",
                                action_id="test action id",
                            )]
                        )
                    ]
                )
            )

    def test_swit_response_query_suggestion05(self):
        swit_response = SwitResponse(
            callback_type=SuggestionsCallbackTypes.query_suggestions,
            result=SuggestionsResult(
                option_groups=[
                    OptionGroup(
                        label="test group1",
                        options=[Option(
                            label="test label1",
                            action_id="test action id1",
                        )]
                    ),
                    OptionGroup(
                        label="test group2",
                        options=[Option(
                            label="test label2",
                            action_id="test action id2",
                        )]
                    ),
                ]
            )
        )

        expected: dict = {
            'callback_type': SuggestionsCallbackTypes.query_suggestions,
            'result': {
                'option_groups': [
                    {
                        'label': 'test group1',
                        'options': [{
                            'label': 'test label1',
                            'action_id': 'test action id1'
                        }]
                    },
                    {
                        'label': 'test group2',
                        'options': [{
                            'label': 'test label2',
                            'action_id': 'test action id2'
                        }]
                    }
                ]
            }
        }
        # convert expected json to json format
        expected_json = json.dumps(expected)

        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_query_suggestion06(self):
        swit_response = SwitResponse(
            callback_type=SuggestionsCallbackTypes.query_suggestions,
            result=SuggestionsResult(
                no_options_reason=NoOptionsReason(
                    message="test message",
                )
            )
        )

        expected: dict = {
            'callback_type': SuggestionsCallbackTypes.query_suggestions,
            'result': {
                'no_options_reason': {
                    'message': 'test message'
                }
            }
        }

        # convert expected json to json format
        expected_json = json.dumps(expected)

        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))

    def test_swit_response_task_attachments(self):
        swit_response = SwitResponse(
            callback_type=AttachmentCallbackTypes.share_new_task,
            attachments=[AttachmentView(
                view_id="test01",
                state="test state",
                header=AttachmentHeader(
                    title="this is Header",
                    app_id="test app id",
                    icon=Image(
                        image_url="https://example.com/image.png",
                    )
                ),
                body=AttachmentBody(
                    elements=[TextParagraph(content="test content")],
                ),
            )],
            destination_hint=AttachmentDestinationHint(
                workspace_id="1234",
                project_id="5678",
            )
        )
        expected: dict = {
            'callback_type': 'attachments.share.new_task',
            'attachments': [{
                'view_id': 'test01',
                'state': "test state",
                'header': {
                    'title': 'this is Header',
                    'app_id': 'test app id',
                    'icon': {
                        'type': 'image',
                        'image_url': 'https://example.com/image.png'
                    }
                },
                'body': {
                    'elements': [
                        {
                            'content': 'test content',
                            'markdown': False,
                            'type': 'text'
                        }
                    ],
                }
            }],
            'destination_hint': {
                'workspace_id': '1234',
                'project_id': '5678'
            }
        }
        self.assertEqual(expected, swit_response.model_dump(exclude_none=True))
