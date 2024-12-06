import asyncio
from datetime import date, timedelta
from typing import Any

from attrs import define

from src.logger import logger
from src.services.parsers.cbr_parser import CBRParser
from src.repositories.postgres import PostgresContext
from src.repositories.postgres.data import CurrenciesCRUD


@define
class Parser:
    #: Парсер cbr
    cbr_parser: CBRParser = CBRParser()

    async def load_tomorrow_currencies(self, date_req: date = date.today() + timedelta(days=1)):
        """Метод для загрузки данных о курсе рубля относительно других валют на указанный день"""
        logger.info(f'Start parsing exchange rates for {date_req}')
        currencies: list[dict[str, Any]] = []
        try:
            currencies = [model.model_dump() for model in
                      await self.cbr_parser.get_curr(date_req)]
        except Exception as e:
            logger.error(f"Cannot load currencies on date {date_req}. {e.__class__.__name__}: {e}")

        if len(currencies) > 0:
            db_context = PostgresContext(crud=CurrenciesCRUD())
            try:
                async with db_context.new_session() as session:
                    await db_context.crud.insert_objects(currencies, session=session)
            except Exception as e:
                logger.error(f"Can't save currencies on date {date_req}. {e.__class__.__name__}: {e}")
        logger.info(f'Parsed exchange rates for {date_req} successfully!')


if __name__ == '__main__':
    parser = Parser()
    asyncio.run(parser.load_tomorrow_currencies())