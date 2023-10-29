from abc import abstractmethod, ABC
from typing import List

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from models.users import User


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


class UserRepository(UserRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_info_for_authenticate(self, email: str) -> User:
        query = (
            select(User)
            .where(User.email == email)
            .options(
                load_only(
                    User.id,
                    User.email, User.password, User.is_active,
                ),
            )
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_all(self) -> List[User]:
        query = (
            select(User)
            .where(User.is_active.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one(
            self,
            user_id: int,
    ) -> User:
        query = (
            select(User)
            .where(User.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def create(
            self,
            user_data: dict,
            hashed_password: str,
    ) -> int:
        stmt = (
            insert(User)
            .values(**user_data, password=hashed_password)
            .returning(User.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def is_user_exists_by_email(self, email: str) -> int | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar()

    async def update_win(self, user_id: int) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(win_count=User.win_count + 1)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_lose(self, user_id: int) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(lose_count=User.lose_count + 1)
        )
        await self.session.execute(stmt)
        await self.session.commit()
