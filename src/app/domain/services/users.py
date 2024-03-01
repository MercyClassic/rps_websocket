from collections.abc import Sequence

from fastapi import HTTPException
from starlette import status

from app.application.exceptions.base import NotFound
from app.application.interfaces.managers.users import UserManagerInterface
from app.domain.interfaces.services.users import UserServiceInterface
from app.infrastructure.db.interfaces.repositories.users import UserRepositoryInterface
from app.infrastructure.db.models import User


class UserService(UserServiceInterface):
    def __init__(
            self,
            user_repo: UserRepositoryInterface,
            user_manager: UserManagerInterface,
    ) -> None:
        self.user_repo = user_repo
        self.user_manager = user_manager

    async def authenticate(
            self,
            email: str,
            input_password: str,
    ) -> int:
        user = await self.user_repo.get_info_for_authenticate(email)
        if not user or not self.user_manager.check_password(
                input_password=input_password,
                password_from_db=user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Credentials are not valid',
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Account is not active',
            )
        return user.id

    async def get_users(self) -> Sequence[User]:
        users = await self.user_repo.get_all()
        return users

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_one(user_id)
        if not user:
            raise NotFound
        return user

    async def get_user_by_token(self, token: str) -> User | None:
        user_info = self.user_manager.get_user_info_from_access_token(token)
        user_id = user_info.get('user_id')
        if user_id:
            return await self.get_user(user_id)

    async def create_user(
            self,
            user_data: dict,
    ) -> dict:
        user_data.pop('password1')
        user = await self.user_repo.is_user_exists_by_email(user_data.get('email'))
        if user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='User with this email already exists',
            )
        hashed_password = self.user_manager.make_password(user_data.pop('password2'))
        user_id = await self.user_repo.create(user_data, hashed_password)
        user_data.update({'id': user_id})
        return user_data

    async def update_win(self, user_id: int) -> None:
        await self.user_repo.update_win(user_id)

    async def update_lose(self, user_id: int) -> None:
        await self.user_repo.update_lose(user_id)
