import unittest

from switcore.action.schemas import Body
from switcore.ui.button import Button
from switcore.ui.container import Container
from switcore.ui.datepicker import DatePicker
from switcore.ui.select import Select, Option


class ContainerTest(unittest.TestCase):

    def test_valid01(self):
        body: Body = Body(
            elements=[
                Container(
                    elements=[
                        DatePicker(
                            action_id="action_01",
                            trigger_on_input=False,
                        ),
                        Button(
                            label="Button 1",
                            style="primary_filled"
                        )
                    ]

                )]
        )

        expected = {
            "elements": [
                {
                    "type": "container",
                    "elements": [
                        {
                            "type": "datepicker",
                            "action_id": "action_01",
                            'trigger_on_input': False,
                        },
                        {
                            "type": "button",
                            "label": "Button 1",
                            "style": "primary_filled"
                        }
                    ]
                }
            ]
        }

        self.assertEqual(expected, body.model_dump(exclude_none=True))

    def test_valid02(self):
        select1 = Select(
            placeholder="Select an option",
            trigger_on_input=True,
            options=[
                Option(
                    label="Option 1",
                    action_id="option1"
                ),
                Option(
                    label="Option 2",
                    action_id="option2"
                ),
            ]
        )

        select2 = Select(
            placeholder="Select an option",
            trigger_on_input=True,
            options=[
                Option(
                    label="Option 1",
                    action_id="option11"
                ),
                Option(
                    label="Option 2",
                    action_id="option22"
                ),
            ]
        )

        body: Body = Body(
            elements=[
                Container(
                    elements=[
                        select1,
                        select2
                    ]
                )
            ]
        )

        expected = {
            "elements": [
                {
                    "type": "container",
                    "elements": [
                        {
                            "type": "select",
                            "placeholder": "Select an option",
                            "multiselect": False,
                            "trigger_on_input": True,
                            "options": [
                                {
                                    "label": "Option 1",
                                    "action_id": "option1"
                                },
                                {
                                    "label": "Option 2",
                                    "action_id": "option2",
                                }
                            ],
                            'option_groups': []
                        },
                        {
                            "type": "select",
                            "placeholder": "Select an option",
                            "multiselect": False,
                            "trigger_on_input": True,
                            "options": [
                                {
                                    "label": "Option 1",
                                    "action_id": "option11"
                                },
                                {
                                    "label": "Option 2",
                                    "action_id": "option22",
                                }
                            ],
                            'option_groups': []
                        }
                    ]
                }
            ]
        }

        self.assertEqual(expected, body.model_dump(exclude_none=True))
