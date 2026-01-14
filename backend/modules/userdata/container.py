from dependency_injector import containers, providers
from django.conf import settings

from modules.userdata.factories.profile import ProfileFactory
from modules.userdata.factories.user import UserFactory
from modules.userdata.gateways.jwt import JWTGateway
from modules.userdata.models import User, Profile
from modules.userdata.repositories.user import UserRepository
from modules.userdata.repositories.profile import ProfileRepository
from modules.userdata.serializers.user import UserSerializer
from modules.userdata.serializers.profile import ProfileSerializer
from modules.userdata.use_cases.get_current_user import GetCurrentUserUseCase
from modules.userdata.use_cases.login import LoginUseCase
from modules.userdata.use_cases.refresh_token import RefreshTokenUseCase
from modules.userdata.use_cases.register import RegisterUseCase
from modules.userdata.use_cases.update_profile import UpdateProfileUseCase


class UserDataContainer(containers.DeclarativeContainer):
    # GATEWAYS
    jwt_gateway = providers.Factory(JWTGateway, secret_key=settings.SECRET_KEY)

    # SERIALIZERS
    profile_serializer = providers.Factory(ProfileSerializer)
    user_serializer = providers.Factory(UserSerializer, profile_serializer=profile_serializer)

    # FACTORIES
    profile_factory = providers.Factory(ProfileFactory)
    user_factory = providers.Factory(UserFactory, profile_factory=profile_factory)

    # REPOSITORIES
    profile_repository = providers.Factory(ProfileRepository, model=Profile, profile_factory=profile_factory)
    user_repository = providers.Factory(UserRepository, model=User, user_factory=user_factory, profile_repository=profile_repository)

    # USE CASES
    login_use_case = providers.Factory(
        LoginUseCase,
        user_repository=user_repository,
        jwt_gateway=jwt_gateway,
        user_serializer=user_serializer,
    )

    refresh_token_use_case = providers.Factory(
        RefreshTokenUseCase,
        user_repository=user_repository,
        jwt_gateway=jwt_gateway,
    )

    register_use_case = providers.Factory(
        RegisterUseCase,
        user_repository=user_repository,
        jwt_gateway=jwt_gateway,
        user_serializer=user_serializer,
        profile_repository=profile_repository,
    )

    get_current_user_use_case = providers.Factory(
        GetCurrentUserUseCase,
        user_repository=user_repository,
        user_serializer=user_serializer,
    )

    update_profile_use_case = providers.Factory(
        UpdateProfileUseCase,
        profile_repository=profile_repository,
        profile_serializer=profile_serializer,
    )

