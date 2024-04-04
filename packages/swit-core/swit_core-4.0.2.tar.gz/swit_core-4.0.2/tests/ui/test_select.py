import unittest

from switcore.ui.element_components import OpenLink, Tag, TagStyle
from switcore.ui.image import Image
from switcore.ui.select import Select, Option, OptionGroup, SelectQuery, NoOptionsReason


class SelectTest(unittest.TestCase):

    def test_valid_select01(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1"
                ),
                Option(
                    label="test label2",
                    action_id="action_id2"
                ),
            ]
        )
        expected = {
            'type': 'select',
            'multiselect': False,
            'trigger_on_input': True,
            'options': [
                {
                    'label': 'test label1',
                    'action_id': 'action_id1'
                },
                {
                    'label': 'test label2',
                    'action_id': 'action_id2'
                }
            ],
            'option_groups': []
        }
        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_valid_select02(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1",
                    static_action=OpenLink(
                        link_url="https://www.google.com"
                    )
                ),
                Option(
                    label="test label2",
                    action_id="action_id2"
                ),
            ]
        )
        expected = {
            'type': 'select',
            'multiselect': False,
            'options': [{'action_id': 'action_id1',
                         'label': 'test label1',
                         'static_action': {'link_url': 'https://www.google.com',
                                           'action_type': 'open_link'}},
                        {'action_id': 'action_id2', 'label': 'test label2'}],
            'option_groups': [],
            'trigger_on_input': True,
        }
        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_valid_select03(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1",
                    tag=Tag(content="tag1", style=TagStyle(color='danger'))
                ),
                Option(
                    label="test label2",
                    action_id="action_id2",
                    tag=Tag(content="tag1", style=TagStyle(color='primary', shape='rounded'))
                ),
            ]
        )

        expected = {
            'type': 'select',
            'multiselect': False,
            'options': [{'action_id': 'action_id1', 'label': 'test label1',
                         'tag': {'type': 'tag', 'content': 'tag1',
                                 'style': {'color': 'danger', 'shape': 'rectangular'}}},
                        {'action_id': 'action_id2', 'label': 'test label2',
                         'tag': {'type': 'tag', 'content': 'tag1', 'style': {'color': 'primary', 'shape': 'rounded'}}}],
            'option_groups': [],
            'trigger_on_input': True,
        }
        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_options_select(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    icon=Image(
                        image_url="https://www.google.com",
                    ),
                    action_id="action_id1",
                    tag=Tag(content="tag1"),
                ),
                Option(
                    label="test label2",
                    action_id="action_id2",
                    tag=Tag(content="tag2"),
                ),
                Option(
                    label="test label3",
                    icon=Image(
                        image_url="https://www.google.com",
                    ),
                    action_id="action_id3",
                ),
            ],
            query=SelectQuery(
                query_server=True,
                action_id="action_id"
            )
        )

        expected: dict = {
            'type': 'select',
            'multiselect': False,
            'options': [
                {'action_id': 'action_id1', 'icon': {'type': 'image', 'image_url': 'https://www.google.com'},
                 'label': 'test label1', 'tag': {'type': 'tag', 'content': 'tag1'}},
                {'action_id': 'action_id2', 'label': 'test label2',
                 'tag': {'type': 'tag', 'content': 'tag2'}},
                {'action_id': 'action_id3', 'icon': {'type': 'image', 'image_url': 'https://www.google.com'},
                 'label': 'test label3'}
            ],
            'option_groups': [],
            'trigger_on_input': True,
            'query': {'query_server': True, 'disabled': False, 'action_id': 'action_id'}
        }
        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_group_options_select(self):
        select = Select(
            trigger_on_input=True,
            option_groups=[
                OptionGroup(
                    label="test group1",
                    options=[
                        Option(
                            label="test label1",
                            icon=Image(
                                image_url="https://www.google.com",
                            ),
                            tag=Tag(content="tag1"),
                            action_id="action_id1",
                        ),
                        Option(
                            label="test label2",
                            action_id="action_id2",
                            tag=Tag(content="tag2"),
                        )
                    ],
                ),
                OptionGroup(
                    label="test group2",
                    options=[
                        Option(
                            label="test label3",
                            icon=Image(
                                image_url="https://www.google.com",
                            ),
                            action_id="action_id3",
                        )
                    ],
                ),

            ],
            query=SelectQuery(
                query_server=True,
                action_id="action_id"
            )
        )

        expected: dict = {
            'type': 'select',
            'multiselect': False,
            'options': [],
            'option_groups': [
                {'label': 'test group1', 'options': [
                    {'action_id': 'action_id1', 'icon': {'type': 'image', 'image_url': 'https://www.google.com'},
                     'label': 'test label1', 'tag': {'type': 'tag', 'content': 'tag1'}},
                    {'action_id': 'action_id2', 'label': 'test label2',
                     'tag': {'type': 'tag', 'content': 'tag2'}}
                ]},
                {'label': 'test group2', 'options': [
                    {'action_id': 'action_id3', 'icon': {'type': 'image', 'image_url': 'https://www.google.com'},
                     'label': 'test label3'}
                ]}
            ],
            'trigger_on_input': True,
            'query': {'query_server': True, 'disabled': False, 'action_id': 'action_id'}
        }
        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_mixed_select(self):
        with self.assertRaises(ValueError):
            Select(
                trigger_on_input=True,
                options=[
                    Option(
                        label="test label1",
                        action_id="mixed_action_id1",
                    ),
                    Option(
                        label="test label2",
                        action_id="mixed_action_id2"
                    ),
                ],
                option_groups=[
                    OptionGroup(label="test group1",
                                options=[Option(label="test label1", action_id="mixed_action_id3")]),
                    OptionGroup(label="test group2",
                                options=[Option(label="test label2", action_id="mixed_action_id4")]),
                ],
                query=SelectQuery(
                    action_id="query_action_id_3"
                )
            )

    def test_filter_select(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="filter_action_1",
                ),
                Option(
                    label="test label2",
                    action_id="filter_action_2"
                ),
            ],
            query=SelectQuery(
                query_server=False,
                action_id="query_action_id_4"
            )
        )

        expected: dict = {
            'type': 'select',
            'multiselect': False,
            'options': [{'action_id': 'filter_action_1', 'label': 'test label1'},
                        {'action_id': 'filter_action_2', 'label': 'test label2'}],
            'option_groups': [],
            'trigger_on_input': True,
            'query': {'query_server': False, 'disabled': False, 'action_id': 'query_action_id_4'}

        }

        self.assertEqual(expected, select.model_dump(exclude_none=True))

    def test_select_option_groups_length(self):
        with self.assertRaises(ValueError):
            Select(
                trigger_on_input=True,
                option_groups=[
                    OptionGroup(label="test group1",
                                options=[]),
                    OptionGroup(label="test group2",
                                options=[Option(label="test label2", action_id="mixed_action_id4")]),
                ],
                query=SelectQuery(
                    action_id="query_action_id_3"
                )
            )

    def test_select_no_options_reason(self):
        select = Select(
            trigger_on_input=True,
            no_options_reason=NoOptionsReason(
                message="test message"
            ),
            query=SelectQuery(
                query_server=False,
                action_id="query_action_id_3"
            )
        )

        expected: dict = {
            'type': 'select',
            'multiselect': False,
            'options': [],
            'option_groups': [],
            'trigger_on_input': True,
            'no_options_reason': {'message': 'test message'},
            'query': {'query_server': False, 'disabled': False, 'action_id': 'query_action_id_3'}
        }

        self.assertEqual(expected, select.model_dump(exclude_none=True))
