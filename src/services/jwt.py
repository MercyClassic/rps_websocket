from abc import ABC, abstractmethod

from auth.jwt import generate_jwt, decode_jwt
from config import JWT_ACCESS_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from repositories.jwt import JWTRepository


class JWTServiceInterface(ABC):
    @abstractmethod
    async def create_auth_tokens(self, user_id: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def create_refresh_token(self, user_id: int) -> str:
        raise NotImplementedError

    @abstractmethod
    async def create_access_token(self, user_id: int) -> str:
        raise NotImplementedError

    @abstractmethod
    async def refresh_auth_tokens(self, refresh_token: str):
        raise NotImplementedError

    @abstractmethod
    async def delete_refresh_token(self, refresh_token: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_user_tokens_if_not_exist(self, token: str, token_data: dict) -> None:
        raise NotImplementedError


class JWTService(JWTServiceInterface):
    def __init__(self, jwt_repo: JWTRepository):
        self.jwt_repo = jwt_repo

    async def create_auth_tokens(self, user_id: int):
        return {
            'access_token': await self.create_access_token(user_id),
            'refresh_token': await self.create_refresh_token(user_id),
        }

    async def create_refresh_token(self, user_id: int) -> str:
        to_encode = {'sub': str(user_id)}
        encoded_jwt = generate_jwt(
            data=to_encode,
            lifetime_seconds=60 * 60 * 24 * 7,
            secret=JWT_REFRESH_SECRET_KEY,
        )
        await self.jwt_repo.save_refresh_token(user_id, encoded_jwt)
        return encoded_jwt

    async def create_access_token(self, user_id: int) -> str:
        is_superuser = await self.jwt_repo.is_superuser(user_id)
        to_encode = {'sub': str(user_id), 'is_superuser': is_superuser}
        return generate_jwt(
            data=to_encode,
            lifetime_seconds=60 * 60,
            secret=JWT_ACCESS_SECRET_KEY,
        )

    async def refresh_auth_tokens(self, refresh_token: str):
        refresh_token_data = decode_jwt(
            encoded_jwt=refresh_token,
            secret=JWT_REFRESH_SECRET_KEY,
        )
        await self.delete_user_tokens_if_not_exist(refresh_token, refresh_token_data)

        tokens = await self.create_auth_tokens(int(refresh_token_data.get('sub')))
        return tokens

    async def delete_refresh_token(self, refresh_token: str) -> None:
        refresh_token_data = decode_jwt(
            encoded_jwt=refresh_token,
            secret=JWT_REFRESH_SECRET_KEY,
            soft=True,
        )
        await self.delete_user_tokens_if_not_exist(refresh_token, refresh_token_data)

    async def delete_user_tokens_if_not_exist(self, token: str, token_data: dict) -> None:
        deleted_id = await self.jwt_repo.delete_refresh_token(token)
        """
        DELETE TOKEN AND RETURNING ID
        IF ID IS NONE THAT MEANS ID WAS DELETED EARLY, MOST LIKELY BY HACKER
        """
        if not deleted_id:
            await self.jwt_repo.delete_all_user_refresh_tokens(int(token_data.get('sub')))
