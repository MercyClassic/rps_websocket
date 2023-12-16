from typing import List

from fastapi import HTTPException
from starlette import status

from exceptions.base import NotFound
from interfaces.services.users import UserServiceInterface
from managers.users import UserManager
from db.models.users import User
from repositories.users import UserRepository


class UserService(UserServiceInterface):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(
            self,
            email: str,
            input_password: str,
    ) -> int:
        user = await self.user_repo.get_info_for_authenticate(email)
        if not user or not UserManager.check_password(
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

    async def get_users(self) -> List[User]:
        data = await self.user_repo.get_all()
        return data

    async def get_user(self, user_id: int) -> User:
        data = await self.user_repo.get_one(user_id)
        if not data:
            raise NotFound
        return data

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
        hashed_password = UserManager.make_password(user_data.pop('password2'))
        user_id = await self.user_repo.create(user_data, hashed_password)
        user_data.update({'id': user_id})
        return user_data
