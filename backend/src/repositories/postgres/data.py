from datetime import date

from attrs import define
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.repositories.postgres.base_crud import BasePostgresCRUD
from src.repositories.sqlalc_models import Currencies
from src.schemas.data_schemas import CurrencyDTO, CurrencyDynamicPoint


@define
class CurrenciesCRUD(BasePostgresCRUD):
    model: Currencies = Currencies

    async def get_currency_by_char_code(
        self, char_code: str, session: AsyncSession
    ) -> CurrencyDTO:
        """ Получение валюты по кодовому символу """
        try:
            query = (
                select(self.model)
                .where(self.model.char_code == char_code)
                .order_by(desc(self.model.data_check))
                .limit(1)
            )
            result = (await session.execute(query)).scalar_one()
        except Exception as e:
            logger.error(
                f"Could not get object by char code '{char_code}': {e.__class__.__name__}: {e}"
            )
            raise

        return CurrencyDTO.model_validate(result, from_attributes=True)

    async def get_exchange_rates(
        self, date_req: date, session: AsyncSession
    ) -> list[CurrencyDTO]:
        """ Получение данных о курсе валют за указанный день """
        try:
            query = select(self.model).where(self.model.data_check == date_req)
            result = (await session.execute(query)).scalars().all()
        except Exception as e:
            logger.error(
                f"Could not get object by date '{date_req}': {e.__class__.__name__}: {e}"
            )
            raise

        if result is None:
            raise ValueError("Currency not found")

        return [CurrencyDTO.model_validate(row, from_attributes=True) for row in result]

    async def check_date_in_db(self, curr_symbol: str, date_req: date, session: AsyncSession) -> bool:
        """Метод для проверки наличия данных в указанный день"""
        try:
            query = select(func.count(self.model.id)).filter(
                and_(
                    self.model.char_code == curr_symbol,
                    self.model.data_check == date_req
                )
            )
            result = (await session.execute(query)).scalar_one()
        except Exception as e:
            logger.error(
                f"Could not get data by date '{date_req}': {e.__class__.__name__}: {e}"
            )
            raise

        return result > 0

    async def get_object_limit_date(
        self, curr_symbol: str, date_left: date, date_right: date, session: AsyncSession
    ) -> list[CurrencyDTO]:
        """ Получение данных по валюте в указанные данные """
        try:
            query = select(self.model).where(
                and_(
                    self.model.char_code == curr_symbol,
                    self.model.data_check >= date_left,
                    self.model.data_check <= date_right,
                )
            )
            result = (await session.execute(query)).scalars().all()
        except Exception as e:
            logger.error(
                f"Could not get object by date borders ({date_left, date_right}): {e.__class__.__name__}: {e}"
            )
            raise

        if result is None:
            raise ValueError("Currency not found")

        return [
            CurrencyDynamicPoint.model_validate(row, from_attributes=True)
            for row in result
        ]
