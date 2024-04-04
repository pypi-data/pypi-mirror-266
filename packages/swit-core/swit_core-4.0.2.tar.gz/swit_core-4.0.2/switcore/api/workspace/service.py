from switcore.api.helpers import sort_by_name
from switcore.api.workspace.schemas import Workspace
from switcore.httpclient import CustomHTTPClient


@sort_by_name
def get_sync_all_workspaces_recursive(
        http_client: CustomHTTPClient,
        offset: str | None = None  # type: ignore
) -> list[Workspace]:
    params: dict = {
        "limit": 50,
    }

    if offset:
        params["offset"] = offset

    res = http_client.api_get('/v1/api/workspace.list', params=params)

    data: dict = res.json()
    data = data.get('data', {})

    workspaces_data: list[dict] = data.get('workspaces', [])
    new_offset: str | None = data.get('offset', None)

    if len(workspaces_data) == 0:
        return []

    workspaces = [Workspace(**workspace) for workspace in workspaces_data]
    next_workspaces = get_sync_all_workspaces_recursive(http_client, new_offset)
    return workspaces + next_workspaces


def get_sync_workspace(
        http_client: CustomHTTPClient,
        workspace_id: str) -> Workspace | None:
    params: dict = {
        "id": workspace_id,
    }

    res = http_client.api_get('/v1/api/workspace.info', params=params)

    data: dict = res.json()
    data = data.get('data', {})

    workspaces_data: dict | None = data.get('workspace', None)

    if workspaces_data is None:
        return None

    return Workspace(**workspaces_data)
