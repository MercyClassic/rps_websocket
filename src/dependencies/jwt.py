from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from config import Config
from db.database import get_session_stub
from dependencies.stub import Stub
from encoders.jwt import JWTEncoder
from interfaces.encoders.jwt import JWTEncoderInterface
from repositories.jwt import JWTRepository
from services.jwt import JWTService


def get_jwt_service(
        session: Annotated[AsyncSession, Depends(get_session_stub)],
        jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
        config: Annotated[Config, Depends(Stub(Config))],
):
    return JWTService(
        JWTRepository(session),
        jwt_encoder,
        config.JWT_REFRESH_SECRET_KEY,
        config.JWT_ACCESS_SECRET_KEY,
    )


def get_jwt_encoder(
        config: Annotated[Config, Depends(Stub(Config))],
):
    return JWTEncoder(
        config.ALGORITHM,
    )


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
