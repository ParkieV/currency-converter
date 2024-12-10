import asyncio
from datetime import date, timedelta
from typing import Any

from attrs import define

from src.logger import logger
from src.repositories.postgres import PostgresContext
from src.repositories.postgres.data import CurrenciesCRUD
from src.services.parsers.cbr_parser import CBRParser
from src.services.parsers.dadata_parser import DadataParser


@define(kw_only=True)
class Parser:
    #: Парсер cbr
    _cbr_parser: CBRParser | None = None

    #: Парсер Dadata
    _dadata_parser: DadataParser | None = None

    @property
    def cbr_parser(self) -> CBRParser:
        """ Геттер класса `CBRParser` """
        if self._cbr_parser is None:
            raise ValueError("CBR parser not initialized")

        return self._cbr_parser

    @property
    def dadata_parser(self) -> DadataParser:
        """ Геттер класса `DadataParser` """
        if self._dadata_parser is None:
            raise ValueError("Dadata parser not initialized")

        return self._dadata_parser

    async def load_tomorrow_currencies(
        self, date_req: date = date.today() + timedelta(days=1)
    ) -> None:
        """
        Метод для загрузки данных о курсе рубля относительно других валют на указанный день

        :param date_req: за какую дату необходимо получить данные

        :return: данные о курсе валют за указанный день
        """
        logger.info(f"Start parsing exchange rates for {date_req}")
        currencies: list[dict[str, Any]] = []
        try:
            currencies = [
                model.model_dump() for model in await self.cbr_parser.get_curr(date_req)
            ]
        except Exception as e:
            logger.error(
                f"Cannot load currencies on date {date_req}. {e.__class__.__name__}: {e}"
            )

        if len(currencies) > 0:
            db_context = PostgresContext(crud=CurrenciesCRUD())
            try:
                async with db_context.new_session() as session:
                    await db_context.crud.insert_objects(currencies, session=session)
            except Exception as e:
                logger.error(
                    f"Can't save currencies on date {date_req}. {e.__class__.__name__}: {e}"
                )
        logger.info(f"Parsed exchange rates for {date_req} successfully!")

    async def get_gov_currency_data(self, country: str) -> list[dict[str, Any]]:
        """
        Метод для получения информации о государственной валюте указанной страны

        :param country: страна

        :return: информация о валюте
        """
        countries = await self.dadata_parser.fulltext_currency_search(country)

        for i, country in enumerate(countries):
            data = country.get("data")
            if data is None:
                logger.info(f"Could not find country data for {i}")
                continue

            curr_symbol = data.get("strcode")

            if curr_symbol is None:
                logger.info(f"Could not find country currency symbol for {i}")
                continue

            db_context = PostgresContext(crud=CurrenciesCRUD())
            try:
                async with db_context.new_session() as session:
                    cdr_id = (
                        await db_context.crud.get_currency_by_char_code(
                            curr_symbol, session
                        )
                    ).cdr_id
            except Exception:
                logger.debug(f"Could not find currency with char code '{curr_symbol}'.")
                cdr_id = None

            country["data"]["cdr_id"] = cdr_id

        return countries


if __name__ == "__main__":
    parser = Parser(cbr_parser=CBRParser())
    asyncio.run(parser.load_tomorrow_currencies())
