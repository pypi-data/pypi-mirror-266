from collections import defaultdict
from urllib.parse import quote, unquote

from switcore.type import AsyncDrawerHandler


def escape(text: str) -> str:
    return quote(unquote(text), safe='')


class PathResolver:
    def __init__(self, action_id: str, paths: list[int | str] | None = None) -> None:
        if paths is None:
            paths = []

        self._escaped_action_id: str = escape(action_id)
        self._escaped_paths: list[str] = []
        for path in paths:
            self._add_path(path)

    def __str__(self):
        return self.combined_path

    @property
    def combined_path(self) -> str:
        """
        :return escaped action_id + escaped paths string
        """
        escaped: str = '/'.join(self._escaped_paths)
        return f'{self._escaped_action_id}/{escaped}'

    @property
    def id(self) -> str:
        return unquote(self._escaped_action_id)

    @property
    def key(self) -> str:
        """
        :return: escaped action_id
        """
        return self._escaped_action_id

    @property
    def paths(self) -> list[int | str]:
        ret: list[int | str] = []
        for path in self._escaped_paths:
            if path.isdigit():
                ret.append(int(path))
            else:
                ret.append(unquote(path))

        return ret

    @staticmethod
    def from_combined(combined: str) -> 'PathResolver':
        """
        :param combined: escaped action_id + escaped paths
        """
        arr: list[str] = combined.split('/')
        paths: list[str] = arr[1:]

        if len(paths) == 1 and paths[0] == '':
            paths = []

        return PathResolver(arr[0], paths)  # type: ignore

    def _add_path(self, path: int | str):
        assert isinstance(path, int) or isinstance(path, str), "only int or str is allowed"

        self._escaped_paths.append(escape(str(path)))


class ActivityRouter:

    def __init__(self) -> None:
        self.handlers: dict[str, AsyncDrawerHandler] = dict()
        self.view_actions: dict[str, set[str]] = defaultdict(set)

    def register(self, action_id: str, view_ids: list[str] | None = None):
        def decorator(func):
            escaped_action_id = escape(action_id)
            self.handlers[escaped_action_id] = func

            if view_ids is None:
                self.view_actions[escaped_action_id].add('*')
            else:
                for view_id in view_ids:
                    self.view_actions[escaped_action_id].add(escape(view_id))

            return func

        return decorator
