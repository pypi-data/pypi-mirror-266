from httpx import Response

from switcore.api.channel.schemas import Channel
from switcore.api.helpers import sort_by_name
from switcore.httpclient import CustomHTTPClient


@sort_by_name
def get_sync_all_channels_recursive(
        http_client: CustomHTTPClient,
        workspace_id: str,
        offset: str | None = None  # type: ignore
) -> list[Channel]:
    params: dict = {
        "limit": 50,
        "workspace_id": workspace_id,
        "type": "gen,dfl"
    }

    if offset:
        params["offset"] = offset

    res = http_client.api_get('/v1/api/channel.list', params=params)

    data: dict = res.json()
    data = data.get('data', {})

    channels_data: list[dict] = data.get('channels', [])
    new_offset: str | None = data.get('offset', None)

    if len(channels_data) == 0:
        return []

    channels = [Channel(**channel) for channel in channels_data]
    next_channels = get_sync_all_channels_recursive(http_client, workspace_id, new_offset)
    return channels + next_channels


def get_sync_channel_user_list(
        http_client: CustomHTTPClient,
        channel_id: str,
) -> Response:
    params: dict = {
        "channel_id": channel_id,
    }

    return http_client.api_get('/v1/api/channel.user.list', params=params)


def get_sync_channel(
        http_client: CustomHTTPClient,
        channel_id: str) -> Channel | None:
    params: dict = {
        "id": channel_id,
    }

    res = http_client.api_get('/v1/api/channel.info', params=params)

    data: dict = res.json()
    data = data.get('data', {})

    channel_data: dict | None = data.get('channel', None)

    if channel_data is None:
        return None

    return Channel(**channel_data)
