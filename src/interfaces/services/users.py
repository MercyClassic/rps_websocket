from abc import ABC, abstractmethod
from typing import List

from db.models.users import User


class UserServiceInterface(ABC):
    @abstractmethod
    async def authenticate(
            self,
            email: str,
            input_password: str,
    ) -> int:
        raise NotImplementedError

    async def get_users(self) -> List[User]:
        raise NotImplementedError

    async def get_user(self, user_id: int) -> User:
        raise NotImplementedError

    async def create_user(
            self,
            user_data: dict,
    ) -> dict:
        raise NotImplementedError
