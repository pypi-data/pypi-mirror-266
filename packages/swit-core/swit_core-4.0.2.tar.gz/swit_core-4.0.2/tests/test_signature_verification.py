import time
import unittest

from switcore.auth.signature_verification import SignatureVerifier


class SignatureVerifierTest(unittest.TestCase):
    def setUp(self):
        self.signing_key = "secret_key"
        self.request_body = "test_body"
        self.timestamp = str(int(time.time()))
        self.signature_verifier = SignatureVerifier(self.signing_key)
        self.signature = self.signature_verifier._generate_signature(self.request_body, self.timestamp)

    def test_verification_success(self):
        self.assertTrue(self.signature_verifier.is_valid(self.request_body, self.timestamp, self.signature))

    def test_verification_failure_due_to_time(self):
        expired_timestamp = str(int(time.time()) - 60 * 6)
        self.assertFalse(self.signature_verifier.is_valid(self.request_body, expired_timestamp, self.signature))

    def test_verification_failure_due_to_invalid_signing_secret(self):
        invalid_secret_key = "invalid_secret_key"
        invalid_signature_verifier = SignatureVerifier(invalid_secret_key)
        self.assertFalse(invalid_signature_verifier.is_valid(self.request_body, self.timestamp, self.signature))
