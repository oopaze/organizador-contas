from datetime import datetime, timezone
from unittest.mock import patch

import jwt
from django.test import SimpleTestCase

from modules.userdata.gateways.jwt import JWTGateway


class TestJWTGatewayExpiry(SimpleTestCase):
    def setUp(self):
        self.gateway = JWTGateway(secret_key="test-secret")

    def test_access_token_lasts_at_least_one_week(self):
        token = self.gateway.generate_access_token(user_id=1, email="u@u.com")
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])

        lifetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) - datetime.fromtimestamp(
            payload["iat"], tz=timezone.utc
        )

        self.assertGreaterEqual(lifetime.days, 7)

    def test_refresh_token_lasts_longer_than_access(self):
        token = self.gateway.generate_refresh_token(user_id=1, email="u@u.com")
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])

        lifetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) - datetime.fromtimestamp(
            payload["iat"], tz=timezone.utc
        )

        self.assertGreater(lifetime.days, self.gateway.access_token_expiry_days)
