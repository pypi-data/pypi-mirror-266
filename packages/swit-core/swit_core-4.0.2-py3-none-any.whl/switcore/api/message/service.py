import json
import os

from httpx import Response

from switcore.async_httpclient import CustomAsyncHTTPClient
from switcore.httpclient import CustomHTTPClient
from switcore.logger import get_logger

logger = get_logger()


async def create_message(
        http_client: CustomAsyncHTTPClient,
        channel_id: str,
        content: dict,
        attachments: list[dict]
):
    app_id: str | None = os.getenv('APPS_ID', None)

    assert app_id is not None, "check APPS_ID in env!!"

    data = {
        'channel_id': channel_id,
        'body_type': 'json_string',
        'content': json.dumps(content),
        'app_id': app_id,
    }

    if len(attachments) > 0:
        data['attachments'] = attachments  # type: ignore

    try:
        response: Response = await http_client.api_post(
            path="/v1/api/message.create",
            data=data
        )
    except Exception as e:
        raise e

    if response.status_code == 200:
        logger.info(f"successful payload is {data}")
    else:
        logger.info(f"failed payload is {data} {response.status_code} {response.text}")
    return response


def create_sync_message(
        http_client: CustomHTTPClient,
        channel_id: str,
        content: dict,
        attachments: list[dict]
):
    app_id: str | None = os.getenv('APPS_ID', None)

    assert app_id is not None, "check APPS_ID in env!!"

    data = {
        'channel_id': channel_id,
        'body_type': 'json_string',
        'content': json.dumps(content),
        'app_id': app_id,
    }

    if len(attachments) > 0:
        data['attachments'] = attachments  # type: ignore

    try:
        response: Response = http_client.api_post(
            path="/v1/api/message.create",
            data=data
        )
    except Exception as e:
        raise e

    if response.status_code == 200:
        logger.info(f"successful payload is {data}")
    else:
        logger.info(f"failed payload is {data} {response.status_code} {response.text}")
    return response
