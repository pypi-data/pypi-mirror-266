from abc import ABC
from collections import defaultdict

from switcore.action.activity_router import ActivityRouter
from switcore.type import AsyncDrawerHandler, DrawerHandler


class BaseHandler(ABC):
    def __init__(self) -> None:
        self._handlers: dict[str, AsyncDrawerHandler | DrawerHandler] = dict()
        self._view_actions: dict[str, set[str]] = defaultdict(set)

    def include_activity_router(self, activity_router: ActivityRouter):
        self._view_actions.update(activity_router.view_actions)
        for action_id, func in activity_router.handlers.items():
            self.add_handler(action_id, func)

    def add_handler(self, action_id: str, func: AsyncDrawerHandler | DrawerHandler):
        self._handlers[action_id] = func

    def get_handler(self, action_id: str) -> AsyncDrawerHandler | DrawerHandler:
        return self._handlers[action_id]
