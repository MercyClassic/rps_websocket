from typing import Annotated

from fastapi import Depends

from config import Config
from dependencies.jwt import get_access_token_from_headers
from dependencies.stub import Stub
from interfaces.encoders.jwt import JWTEncoderInterface
from managers.users import UserManager


async def get_current_user_info(
        access_token: Annotated[str, Depends(get_access_token_from_headers)],
        jwt_encoder: Annotated[JWTEncoderInterface, Depends()],
        config: Annotated[Config, Depends(Stub(Config))],
) -> dict:
    user_manager = UserManager(config.JWT_ACCESS_SECRET_KEY, jwt_encoder)
    return user_manager.get_user_info_from_access_token(access_token)
