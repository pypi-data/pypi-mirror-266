import inspect
from typing import Callable

from switcore.api.channel.schemas import Channel
from switcore.api.workspace.schemas import Workspace


def sort_by_name(func: Callable) -> Callable:
    def sync_wrapper(*args, **kwargs) -> list[Workspace | Channel]:
        arr: list[Workspace | Channel] = func(*args, **kwargs)
        return sort_and_return(arr)

    async def async_wrapper(*args, **kwargs) -> list[Workspace | Channel]:
        arr: list[Workspace | Channel] = await func(*args, **kwargs)
        return sort_and_return(arr)

    def sort_and_return(arr: list[Workspace | Channel]) -> list[Workspace | Channel]:
        if len(arr) > 0 and hasattr(arr[0], "name"):
            arr.sort(key=lambda element: getattr(element, "name"))
        return arr

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
