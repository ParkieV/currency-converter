from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.baked import Result

from src.logger import logger
from src.repositories.sqlalc_models import Base

BaseDBModel = TypeVar("BaseDBModel", bound=type(Base))
ModelDTO = TypeVar("ModelDTO", bound=BaseModel)


@define
class BasePostgresCRUD:

    model: BaseDBModel | None = None

    async def get_object_by_id(
        self, model_id: int, out_schema: ModelDTO | None, *, session: AsyncSession
    ) -> ModelDTO:
        """Получение объекта в БД по ID"""
        result: Result | None = None

        try:
            result = await session.execute(
                select(self.model).where(self.model.id == model_id)
            )
        except Exception as e:
            logger.error(
                f"Could not get object by id '{model_id}': {e.__class__.__name__}: {e}"
            )

        if result is None:
            raise ValueError("User not found")

        return out_schema.model_validate(result)

    @classmethod
    async def get_objects(
        cls,
        out_schema: ModelDTO | None,
        offset: int | None = None,
        limit: int | None = None,
        *,
        session: AsyncSession,
    ) -> list[ModelDTO]:
        query = select(cls.model)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        try:
            result = (await session.execute(query)).all()
        except Exception as e:
            logger.error(f"Could not get objects: {e.__class__.__name__}: {e}")
            raise

        return [out_schema.model_validate(row, from_attributes=True) for row in result]

    async def insert_objects(
        self, new_objects: list[Mapping[str, Any]], session: AsyncSession
    ) -> None:
        """Добавление объекта в БД"""
        new_models = []
        try:
            new_models = [self.model(**new_object) for new_object in new_objects]
        except Exception as e:
            logger.error(f"Could not transform object. {e.__class__.__name__}: {e}")
        try:
            session.add_all(new_models)
            await session.flush()
        except Exception as e:
            logger.error(
                f"Could not insert object in database: {e.__class__.__name__}: {e}"
            )
            raise
