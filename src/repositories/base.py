from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only


class AbstractRepository(ABC):

    @abstractmethod
    async def return_author_id(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(
            self,
            session: AsyncSession,
            pagination_params: dict = None,
    ):
        if not pagination_params:
            pagination_params = {'limit': 10, 'offset': 0}
        self.session = session
        self.limit = pagination_params.get('limit')
        self.offset = pagination_params.get('offset')

    def paginate_query(self, query):
        return query.offset(self.offset).limit(self.limit)

    async def return_author_id(self, instance_id: int):
        query = (
            select(self.model)
            .where(self.model.id == instance_id)
            .options(load_only(self.model.user_id))
        )
        instance = await self.session.execute(query)
        return instance.scalar_one()

    async def create(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_one(self, instance_id: int):
        query = select(self.model).where(self.model.id == instance_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_all(self):
        query = select(self.model)
        query = self.paginate_query(query)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, instance_id: int, update_data: dict):
        stmt = (
            update(self.model)
            .where(self.model.id == instance_id)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete(self, instance_id: int):
        stmt = delete(self.model).where(self.model.id == instance_id)
        await self.session.execute(stmt)
        await self.session.commit()
