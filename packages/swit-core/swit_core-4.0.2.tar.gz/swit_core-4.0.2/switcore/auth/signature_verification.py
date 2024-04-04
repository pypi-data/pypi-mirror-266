import hmac
import hashlib
from time import time


class SignatureVerifier:
    def __init__(self, signing_key: str, max_delay: int = 60 * 5, secret_version: str = "s0="):
        self.signing_key = signing_key.encode()
        self.max_delay = max_delay
        self.secret_version = secret_version

    def is_valid(self, body: str, timestamp_or_null: str | None, signature_or_null: str | None) -> bool:
        if None in [body, timestamp_or_null, signature_or_null]:
            return False

        assert signature_or_null is not None, "signature_or_null is None"
        assert timestamp_or_null is not None, "timestamp_or_null is None"

        if self._is_timestamp_valid(timestamp_or_null):
            calculated_signature = self._generate_signature(body, timestamp_or_null)
            return hmac.compare_digest(calculated_signature, signature_or_null)
        return False

    def _is_timestamp_valid(self, timestamp: str) -> bool:
        return abs(time() - int(timestamp)) <= self.max_delay

    def _generate_signature(self, body: str, timestamp: str) -> str:
        base_string = f"swit:{timestamp}:{body}"
        signature = hmac.new(self.signing_key, base_string.encode(), hashlib.sha256)
        return self.secret_version + signature.hexdigest()
