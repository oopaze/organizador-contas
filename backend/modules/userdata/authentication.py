from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from modules.userdata.gateways.jwt import JWTGateway
from modules.userdata.models import User


class JWTAuthentication(BaseAuthentication):
    PREFIX = "Bearer"

    def __init__(self):
        self.jwt_gateway = JWTGateway(secret_key=settings.SECRET_KEY)

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != self.PREFIX.lower():
            return None

        token = parts[1]
        payload = self.jwt_gateway.validate_access_token(token)
        if not payload:
            raise AuthenticationFailed("Invalid or expired token")

        try:
            user = User.objects.get(id=payload["user_id"], is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, token)
