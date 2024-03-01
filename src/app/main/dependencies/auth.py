from typing import Annotated

from fastapi import Depends

from app.application.interfaces.managers.users import UserManagerInterface
from app.main.dependencies.jwt import get_access_token_from_headers


async def get_current_user_info(
        access_token: Annotated[str, Depends(get_access_token_from_headers)],
        user_manager: Annotated[UserManagerInterface, Depends()],
) -> dict:
    return user_manager.get_user_info_from_access_token(access_token)
