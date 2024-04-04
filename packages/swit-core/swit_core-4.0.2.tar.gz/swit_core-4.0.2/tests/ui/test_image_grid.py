import unittest

from switcore.ui.interactive_image import InteractiveImage
from switcore.ui.image_grid import ImageGrid


class InteractiveImageTest(unittest.TestCase):

    def test_valid_interactive_image01(self):
        expected: dict = {
            "type": "image_grid",
            "images": [
                {
                    "alt": "image test",
                    "type": "interactive_image",
                    "action_id": "action_01",
                    "draggable": False,
                    "image_url": "https://www.example.com/images/sample.png"
                }
            ],
            "column_count": 2
        }

        image = InteractiveImage(
            image_url="https://www.example.com/images/sample.png",
            alt="image test",
            action_id="action_01"
        )
        grid = ImageGrid(
            images=[image],
            column_count=2
        )
        actual: dict = grid.model_dump(exclude_none=True)
        self.assertEqual(expected, actual)

    def test_valid_interactive_image02(self):
        expected: dict = {
            "type": "image_grid",
            "images": [
                {
                    "alt": "image test1",
                    "type": "interactive_image",
                    "action_id": "action_01",
                    "draggable": False,
                    "image_url": "https://www.example.com/images/sample1.png"
                },
                {
                    "alt": "image test2",
                    "type": "interactive_image",
                    "action_id": "action_02",
                    "draggable": True,
                    "image_url": "https://www.example.com/images/sample2.png"
                },
            ],
            "column_count": 3
        }

        image1 = InteractiveImage(
            image_url="https://www.example.com/images/sample1.png",
            alt="image test1",
            action_id="action_01"
        )
        image2 = InteractiveImage(
            image_url="https://www.example.com/images/sample2.png",
            alt="image test2",
            action_id="action_02",
            draggable=True
        )
        grid = ImageGrid(
            images=[image1, image2],
            column_count=3
        )

        actual: dict = grid.model_dump(exclude_none=True)

        self.assertEqual(expected, actual)
