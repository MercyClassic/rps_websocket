from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.application.interfaces.managers.users import UserManagerInterface
from app.application.managers.users import UserManager
from app.domain.services.users import UserService
from app.infrastructure.db.database import get_session_stub
from app.infrastructure.db.repositories.users import UserRepository
from app.main.config import Config
from app.main.dependencies.stub import Stub


def get_user_manager(
        jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
        config: Annotated[Config, Depends(Stub(Config))],
) -> UserManager:
    return UserManager(
        jwt_access_secret_key=config.JWT_ACCESS_SECRET_KEY,
        jwt_encoder=jwt_encoder,
    )


def get_user_service(
        session: Annotated[AsyncSession, Depends(get_session_stub)],
        manager: Annotated[UserManagerInterface, Depends()],
) -> UserService:
    return UserService(UserRepository(session), manager)
