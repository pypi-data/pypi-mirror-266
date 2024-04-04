from switcore.api.user.schemas import SwitUser
from switcore.async_httpclient import CustomAsyncHTTPClient
from switcore.httpclient import CustomHTTPClient


async def get_me(http_client: CustomAsyncHTTPClient) -> SwitUser | None:
    res = await http_client.api_get('/v1/api/user.info')

    data: dict = res.json()
    data = data.get('data', {})

    user_data: dict | None = data.get('user', None)

    if user_data is None:
        return None

    return SwitUser(**user_data)


def get_sync_me(http_client: CustomHTTPClient) -> SwitUser | None:
    res = http_client.api_get('/v1/api/user.info')

    data: dict = res.json()
    data = data.get('data', {})

    user_data: dict | None = data.get('user', None)

    if user_data is None:
        return None

    return SwitUser(**user_data)
