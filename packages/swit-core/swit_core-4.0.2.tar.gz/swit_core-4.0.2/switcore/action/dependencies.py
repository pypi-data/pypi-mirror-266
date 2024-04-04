import os

from starlette.requests import Request

from switcore.action.schemas import SwitRequest
from switcore.auth.exception import VerificationFailedException
from switcore.auth.signature_verification import SignatureVerifier
from switcore.logger import get_logger

logger = get_logger()


async def get_swit_request(
        request: Request,
):
    swit_singing_key: str | None = os.getenv('SWIT_SINGING_KEY', None)

    assert swit_singing_key is not None, "SWIT_SINGING_KEY is not set check .env file"

    verifier = SignatureVerifier(signing_key=swit_singing_key)

    timestamp_or_null: str | None = request.headers.get("x-swit-request-timestamp", None)
    signature_or_null: str | None = request.headers.get("x-swit-signature", None)

    body = await request.body()

    if not verifier.is_valid(body.decode(), timestamp_or_null, signature_or_null):
        raise VerificationFailedException("Verification failed check your signing key")

    data: dict = await request.json()
    logger.info(data)
    return SwitRequest(**data)
