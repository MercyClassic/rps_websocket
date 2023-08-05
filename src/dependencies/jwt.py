from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from db.database import get_async_session
from repositories.jwt import JWTRepository
from services.jwt import JWTService


def get_jwt_service(session: AsyncSession = Depends(get_async_session)):
    return JWTService(JWTRepository(session))


async def get_access_token_from_headers(request: Request) -> str:
    return request.headers.get('Authorization')
