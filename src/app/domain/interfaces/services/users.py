from abc import ABC, abstractmethod

from app.infrastructure.db.models import User


class UserServiceInterface(ABC):
    @abstractmethod
    async def authenticate(
            self,
            email: str,
            input_password: str,
    ) -> int:
        raise NotImplementedError

    async def get_users(self) -> list[User]:
        raise NotImplementedError

    async def get_user(self, user_id: int) -> User:
        raise NotImplementedError

    async def get_user_by_token(self, token: str) -> User:
        raise NotImplementedError

    async def create_user(
            self,
            user_data: dict,
    ) -> dict:
        raise NotImplementedError

    async def update_win(self, user_id: int) -> None:
        raise NotImplementedError

    async def update_lose(self, user_id: int) -> None:
        raise NotImplementedError
