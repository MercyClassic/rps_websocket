from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.application.encoders.jwt import JWTEncoder
from app.application.interfaces.encoders.jwt import JWTEncoderInterface
from app.domain.services.jwt import JWTService
from app.infrastructure.db.database import get_session_stub
from app.infrastructure.db.repositories.jwt import JWTRepository
from app.main.config import Config
from app.main.dependencies.stub import Stub


def get_jwt_service(
        session: Annotated[AsyncSession, Depends(get_session_stub)],
        jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
        config: Annotated[Config, Depends(Stub(Config))],
) -> JWTService:
    return JWTService(
        JWTRepository(session),
        jwt_encoder,
        config.JWT_REFRESH_SECRET_KEY,
        config.JWT_ACCESS_SECRET_KEY,
    )


def get_jwt_encoder(
        config: Annotated[Config, Depends(Stub(Config))],
) -> JWTEncoder:
    return JWTEncoder(
        config.ALGORITHM,
    )


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
