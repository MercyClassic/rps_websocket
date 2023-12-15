from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from config import Config, get_config
from db.database import get_session_stub
from repositories.jwt import JWTRepository
from services.jwt import JWTService


def get_jwt_service(
        session: Annotated[AsyncSession, Depends(get_session_stub)],
        config: Annotated[Config, Depends(get_config)],
):
    return JWTService(
        JWTRepository(session),
        config.JWT_REFRESH_SECRET_KEY,
        config.JWT_ACCESS_SECRET_KEY,
    )


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
