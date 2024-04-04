import unittest

from switcore.ui.info_card import InfoCard
from switcore.ui.item import Item
from switcore.ui.text_paragraph import TextParagraph


class InfoCardTest(unittest.TestCase):

    def test_valid(self):
        text = TextParagraph(
            content="test content"
        )

        item = Item(
            label='test',
            text=text
        )

        info_card = InfoCard(
            action_id='test_action_id',
            draggable=True,
            items=[item])

        expected = {
            'type': 'info_card',
            'action_id': 'test_action_id',
            'draggable': True,
            'items': [
                {
                    'label': 'test',
                    'text': {
                        'content': 'test content',
                        'markdown': False,
                        'type': 'text'
                    }
                }
            ]
        }

        self.assertEqual(expected, info_card.model_dump(exclude_none=True))
