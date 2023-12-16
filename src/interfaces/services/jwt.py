from abc import ABC, abstractmethod


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
