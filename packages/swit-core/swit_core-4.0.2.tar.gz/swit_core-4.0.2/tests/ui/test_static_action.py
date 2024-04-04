import unittest

from switcore.ui.button import Button
from switcore.ui.element_components import WriteToClipboard, OpenLink, CloseView


class StaticActionTest(unittest.TestCase):

    def test_clipboard_copy(self):
        button = Button(
            label="button",
            static_action=WriteToClipboard(
                content="Copied Successfully",
            )
        )
        self.assertTrue(isinstance(button.static_action, WriteToClipboard))
        expected = {
            'label': 'button',
            'static_action': {'action_type': 'write_to_clipboard', 'content': 'Copied Successfully'},
            'type': 'button'
        }
        self.assertEqual(expected, button.model_dump(exclude_none=True))

    def test_open_link(self):
        button = Button(
            label="button",
            static_action=OpenLink(
                link_url="https://www.google.com",
            )
        )
        expected = {
            'label': 'button',
            'static_action': {'action_type': 'open_link', 'link_url': 'https://www.google.com'},
            'type': 'button'
        }
        self.assertEqual(expected, button.model_dump(exclude_none=True))

    def test_close_view(self):
        button = Button(
            label="button",
            static_action=CloseView()
        )
        self.assertTrue(isinstance(button.static_action, CloseView))

        expected = {
            'label': 'button',
            'static_action': {'action_type': 'close_view'},
            'type': 'button'
        }
        self.assertEqual(expected, button.model_dump(exclude_none=True))
