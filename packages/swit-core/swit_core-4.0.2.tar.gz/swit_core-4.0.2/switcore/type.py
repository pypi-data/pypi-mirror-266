from typing import Callable, Awaitable

from switcore.action.schemas import SwitResponse

AsyncDrawerHandler = Callable[..., Awaitable[SwitResponse]]
DrawerHandler = Callable[..., SwitResponse]
