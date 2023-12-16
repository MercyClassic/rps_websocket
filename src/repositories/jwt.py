from sqlalchemy import select, insert, delete
from sqlalchemy.orm import load_only

from interfaces.repositories.jwt import JWTRepositoryInterface
from db.models.jwt import RefreshToken
from db.models.users import User


class JWTRepository(JWTRepositoryInterface):

    def __init__(self, session):
        self.session = session

    async def is_superuser(self, user_id: int) -> bool:
        query = select(User).where(User.id == user_id).options(load_only(User.is_superuser))
        result = await self.session.execute(query)
        return result.scalar_one().is_superuser

    async def save_refresh_token(self, user_id: int, token: str) -> None:
        stmt = insert(RefreshToken).values(user_id=user_id, token=token)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_refresh_token(self, token: str) -> int | None:
        stmt = (
            delete(RefreshToken)
            .where(RefreshToken.token == token)
            .returning(RefreshToken.id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_all_user_refresh_tokens(self, user_id) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()
