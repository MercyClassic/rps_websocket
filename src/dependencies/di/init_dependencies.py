from fastapi import FastAPI

from config import Config, load_config
from db.database import get_async_session, get_session_stub
from dependencies.jwt import get_jwt_service, get_jwt_encoder
from dependencies.users import get_user_service

from interfaces.encoders.jwt import JWTEncoderInterface
from interfaces.services.jwt import JWTServiceInterface
from interfaces.services.users import UserServiceInterface


def init_dependencies(app: FastAPI) -> None:
    app.dependency_overrides[get_session_stub] = get_async_session
    app.dependency_overrides[JWTEncoderInterface] = get_jwt_encoder
    app.dependency_overrides[JWTServiceInterface] = get_jwt_service
    app.dependency_overrides[UserServiceInterface] = get_user_service
    app.dependency_overrides[Config] = load_config
