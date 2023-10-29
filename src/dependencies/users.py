from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session_stub
from repositories.users import UserRepository
from services.users import UserService


def get_user_service(
        session: Annotated[AsyncSession, Depends(get_session_stub)],
):
    return UserService(UserRepository(session))
