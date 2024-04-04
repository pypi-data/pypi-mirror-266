import unittest

from switcore.ui.element_components import OpenOauthPopup
from switcore.ui.interactive_image import InteractiveImage


class InteractiveImageTest(unittest.TestCase):

    def test_valid_interactive_image01(self):
        expected: dict = {
            "type": "interactive_image",
            "image_url": "https://swit.io/assets/images/home/features/device",
            "alt": "image test",
            "action_id": "action_01",
            "static_action": {
                "action_type": "open_oauth_popup",
                "link_url": "https://example.com"
            },
            "draggable": False
        }

        image = InteractiveImage(
            image_url="https://swit.io/assets/images/home/features/device",
            alt="image test",
            action_id="action_01",
            static_action=OpenOauthPopup(
                link_url="https://example.com"
            )
        )
        actual: dict = image.model_dump(exclude_none=True)
        self.assertEqual(expected, actual)

    def test_valid_interactive_image02(self):
        expected: dict = {
            "type": "interactive_image",
            "image_url": "https://swit.io/assets/images/home/features/device",
            "action_id": "action_01",
            "draggable": True
        }

        image = InteractiveImage(
            image_url="https://swit.io/assets/images/home/features/device",
            action_id="action_01",
            draggable=True
        )
        actual: dict = image.model_dump(exclude_none=True)
        self.assertEqual(expected, actual)
