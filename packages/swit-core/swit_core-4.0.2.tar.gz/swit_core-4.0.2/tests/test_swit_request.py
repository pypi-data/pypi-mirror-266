import json  # noqa: F401
import unittest

from datetime import date, datetime

from switcore.action.schemas import UserActionType, \
    QueryResource, TaskResource, TaskStatus, TaskUser, TaskStatusType, SwitRequest
from tests.utils import create_submit_swit_request, create_query_swit_request, create_task_swit_request


class SwitViewResponseTest(unittest.TestCase):

    def test_swit_submit_request(self):
        swit_request: SwitRequest = create_submit_swit_request("right_panel", "test_action_id01")
        self.assertEqual(swit_request.user_action.type, UserActionType.view_actions_submit)

    def test_swit_query_request(self):
        swit_request: SwitRequest = create_query_swit_request()
        self.assertEqual(swit_request.user_action.type, UserActionType.view_actions_query)
        self.assertTrue(isinstance(swit_request.user_action.resource, QueryResource))

    def test_swit_task_request(self):
        swit_request: SwitRequest = create_task_swit_request()
        self.assertEqual(swit_request.user_action.type, UserActionType.user_commands_context_menus_task.value)
        self.assertTrue(isinstance(swit_request.user_action.resource, TaskResource))
        assert isinstance(swit_request.user_action.resource, TaskResource)
        self.assertEqual(swit_request.user_action.resource.id, "23051106260551ZOVCPS")
        self.assertEqual(swit_request.user_action.resource.parent_task_id, "200302045745598izpK")
        self.assertEqual(swit_request.user_action.resource.title, "Developers documentation")
        self.assertEqual(swit_request.user_action.resource.status, TaskStatus(
            id="220707214090V110qhk",
            name="Done",
            type=TaskStatusType.NOT_STARTED
        ))
        self.assertEqual(swit_request.user_action.resource.assignees, [TaskUser(id="220103011810x7bqTRZ")])
        self.assertEqual(swit_request.user_action.resource.color_label, None)

        # Test with pure date types
        swit_request2 = create_task_swit_request({
            "start_time": "",
            "due_time": "2023-02-14",
            "include_time": False
        })
        due_time = swit_request2.user_action.resource.period.due_time
        self.assertTrue(isinstance(due_time, date))
