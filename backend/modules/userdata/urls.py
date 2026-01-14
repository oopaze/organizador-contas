from django.urls import path

from modules.userdata.views import LoginView, MeView, RefreshTokenView, RegisterView, UpdateProfileView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("user/register/", RegisterView.as_view(), name="register"),
    path("user/me/", MeView.as_view(), name="me"),
    path("user/me/profile/", UpdateProfileView.as_view(), name="update_profile"),
]

