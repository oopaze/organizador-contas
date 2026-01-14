from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.userdata.authentication import JWTAuthentication
from modules.userdata.container import UserDataContainer


class LoginView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = UserDataContainer()

    def post(self, request: Request) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = self.container.login_use_case().execute(email, password)
        if not result:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(result, status=status.HTTP_200_OK)


class RegisterView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = UserDataContainer()

    def post(self, request: Request) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = self.container.register_use_case().execute(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        if not result:
            return Response(
                {"error": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_201_CREATED)


class RefreshTokenView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = UserDataContainer()

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = self.container.refresh_token_use_case().execute(refresh_token)
        if not result:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(result, status=status.HTTP_200_OK)


class MeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = UserDataContainer()

    def get(self, request: Request) -> Response:
        result = self.container.get_current_user_use_case().execute(request.user.id)
        if not result:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(result, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = UserDataContainer()

    def patch(self, request: Request) -> Response:
        updated_profile = self.container.update_profile_use_case().execute(
            request.user.profile.id,
            request.data,
        )
        return Response(updated_profile, status=status.HTTP_200_OK)
