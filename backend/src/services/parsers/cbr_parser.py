import xml.etree.ElementTree as ET
from datetime import date, datetime

import aiohttp

from src.schemas.data_schemas import CurrencyDTO, CurrencyDynamicPoint
from src.services.utils import fetch_url


class CBRParser:
    """Парсер для получения данных с сайта cbr.ru"""

    @staticmethod
    async def get_curr(date_req: date) -> list[CurrencyDTO]:
        """
        Метод для получения ставки по валютам за указанный день.

        :param date_req: День, за который будут показаны котировки
        :return: Список котировок за указанный день
        """
        async with aiohttp.ClientSession() as session:
            page_text = await fetch_url(
                url="https://cbr.ru/scripts/XML_daily.asp",
                session=session,
                queries={"date_req": date_req.strftime("%d/%m/%Y")},
            )

        data = ET.fromstring(page_text)

        currencies = [
            CurrencyDTO(
                site="cbr.ru",
                cdr_id=None,
                nominal=1,
                char_code="RUB",
                value=1,
                name="Российский рубль",
                unit_value=1,
            )
        ]
        for valute in data:
            currencies.append(
                CurrencyDTO(
                    site="cbr.ru",
                    cdr_id=valute.get("ID"),
                    nominal=int(valute.find("Nominal").text),
                    char_code=valute.find("CharCode").text,
                    value=float(valute.find("Value").text.replace(",", ".")),
                    name=valute.find("Name").text,
                    unit_value=float(valute.find("VunitRate").text.replace(",", ".")),
                )
            )

        return currencies

    @staticmethod
    async def get_curr_dynamic(curr_code: str, start_date: date, finish_date: date):

        async with aiohttp.ClientSession() as session:
            page_data = await fetch_url(
                f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={start_date.strftime('%d/%m/%Y')}&date_req2={finish_date.strftime('%d/%m/%Y')}&VAL_NM_RQ={curr_code}",
                session,
            )

        data = ET.fromstring(page_data)

        result = []

        for item in data:
            result.append(
                CurrencyDynamicPoint(
                    nominal=int(item.find("Nominal").text),
                    value=float(item.find("Value").text.replace(",", ".")),
                    unit_value=float(item.find("VunitRate").text.replace(",", ".")),
                    date_check=datetime.strptime(item.get("Date"), "%d.%m.%Y").date(),
                )
            )

        return result
