from typing import TypeVar

from fastapi import FastAPI

from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.application.interfaces.managers.users import UserManagerInterface
from app.application.managers.game import BaseGameConnectionManager
from app.domain.interfaces.services.jwt import JWTServiceInterface
from app.domain.interfaces.services.users import UserServiceInterface
from app.infrastructure.db.database import get_async_session, get_session_stub
from app.main.config import Config, load_config
from app.main.dependencies.game import get_game_connection_manager
from app.main.dependencies.jwt import get_jwt_encoder, get_jwt_service
from app.main.dependencies.users import get_user_manager, get_user_service

T = TypeVar('T')


def init_dependencies(app: FastAPI) -> None:
    def singleton(value: T):
        def singleton_factory() -> T:
            return value
        return singleton_factory

    game_connection_manager = get_game_connection_manager()

    app.dependency_overrides[get_session_stub] = get_async_session
    app.dependency_overrides[BaseGameConnectionManager] = singleton(game_connection_manager)
    app.dependency_overrides[UserManagerInterface] = get_user_manager
    app.dependency_overrides[JWTEncoderInterface] = get_jwt_encoder
    app.dependency_overrides[JWTServiceInterface] = get_jwt_service
    app.dependency_overrides[UserServiceInterface] = get_user_service
    app.dependency_overrides[Config] = load_config
