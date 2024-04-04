import unittest

from switcore.ui.datepicker import DatePicker


class DatePickerTest(unittest.TestCase):

    def test_valid(self):
        datepicker = DatePicker(
            action_id='test_action_id',
            placeholder='test_placeholder',
            trigger_on_input=True,
            value='2022-11-23T00:00:00.000Z')

        expected = {
            'type': 'datepicker',
            'action_id': 'test_action_id',
            'placeholder': 'test_placeholder',
            'trigger_on_input': True,
            'value': '2022-11-23T00:00:00.000Z'
        }

        self.assertEqual(expected, datepicker.model_dump(exclude_none=True))
