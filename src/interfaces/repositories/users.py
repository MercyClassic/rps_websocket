from abc import ABC, abstractmethod
from typing import List

from db.models.users import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_info_for_authenticate(self, email: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(
            self,
            user_id: int,
    ) -> User:
        raise NotImplementedError

    @abstractmethod
    async def create(
            self,
            user_data: dict,
            hashed_password: str,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def is_user_exists_by_email(self, email: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    async def update_win(self, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_lose(self, user_id: int) -> None:
        raise NotImplementedError
