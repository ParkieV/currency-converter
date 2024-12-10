from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

import matplotlib.pyplot as plt
import pandas as pd

from src.logger import logger
from src.repositories.postgres import PostgresContext
from src.repositories.postgres.data import CurrenciesCRUD
from src.schemas.data_schemas import CurrencyDinamicDTO
from src.services.parsers import Parser
from src.services.parsers.cbr_parser import CBRParser


async def convert_currencies(from_code: str, to_code: str, value: float):
    """
    Метод для конвертации валюты по курсу ЦБ

    :param from_code: кодовый символ начальной валюты
    :param to_code: кодовый символ конечной валюты
    :param value: количество валюты начальной валюты

    :return: количество валюты конечной валюты
    """
    db_context = PostgresContext(crud=CurrenciesCRUD())
    from_data, to_data = None, None
    async with PostgresContext.new_session() as session:
        try:
            from_data = await db_context.crud.get_currency_by_char_code(
                from_code, session
            )
        except Exception as e:
            logger.error(
                f"Failed to obtain char code for the base currency. {e.__class__.__name__}: {e}"
            )
            raise ValueError("Can't convert from base currency.")

        try:
            to_data = await db_context.crud.get_currency_by_char_code(to_code, session)
        except Exception as e:
            logger.error(
                f"Failed to obtain char code for the target currency. {e.__class__.__name__}: {e}"
            )
            raise ValueError("Can't convert to target currency.")

    return round(from_data.value / to_data.value * value, 4)


async def get_currency_dynamics(curr_symbol: str, start_date: date, finish_date: date):
    """
    Получение динамики изменения валюты

    :param curr_symbol: кодовый символ валюты
    :param start_date: дата начала отслеживания
    :param finish_date: дата конца отслеживания

    :return: список данных о валюте
    """

    db_context = PostgresContext(crud=CurrenciesCRUD())
    async with PostgresContext.new_session() as session:
        try:
            curr_data = await db_context.crud.get_currency_by_char_code(
                curr_symbol, session
            )
        except Exception as e:
            logger.error(
                f"Failed to obtain char code for the base currency. {e.__class__.__name__}: {e}"
            )
            raise ValueError("Can't convert from base currency.")

        if await db_context.crud.check_date_in_db(curr_symbol, start_date, session):
            data = await db_context.crud.get_object_limit_date(
                curr_symbol, start_date, finish_date, session
            )
            resp_model = CurrencyDinamicDTO(
                name=curr_data.name,
                char_code=curr_data.char_code,
                cdr_id=curr_data.cdr_id,
                dynamics=data,
            )
        else:
            parser = Parser(cbr_parser=CBRParser())
            resp_model = CurrencyDinamicDTO(
                name=curr_data.name,
                char_code=curr_data.char_code,
                cdr_id=curr_data.cdr_id,
                dynamics=await parser.cbr_parser.get_curr_dynamic(
                    curr_data.cdr_id, start_date, finish_date
                ),
            )

        return resp_model


def draw_dynamics_graphic(currency_dinamics: CurrencyDinamicDTO) -> Path:
    """
    Получение файла с графиком изменения валюты за указанный период

    :param currency_dinamics: список данных о валюте

    :return: Путь до временного файла с графиком
    """
    df = pd.DataFrame([point.model_dump() for point in currency_dinamics.dynamics])
    df["date_check"] = pd.to_datetime(df["date_check"], format="%Y-%m-%d")
    df = df.sort_values("date_check")

    plt.figure(figsize=(14, 7))
    plt.plot(
        df["date_check"],
        df["unit_value"],
        marker="o",
        linestyle="-",
        color="blue",
        label="Курс USD к RUB",
    )

    title = f"{currency_dinamics.name} ({currency_dinamics.char_code})"
    if currency_dinamics.cdr_id:
        title += f", ID: {currency_dinamics.cdr_id}"
    plt.title(title, fontsize=16)

    plt.xlabel("Дата", fontsize=14)
    plt.ylabel("Курс к RUB", fontsize=14)
    plt.gcf().autofmt_xdate()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    for idx, row in df.iterrows():
        plt.text(
            row["date_check"],
            row["unit_value"] + 0.02,
            f"{row['unit_value']:.4f}",
            fontsize=8,
            ha="center",
        )

    # Сохранение графика в временный файл
    with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        plt.tight_layout()
        plt.savefig(tmp_file.name, format="png")
        plt.close()
        return Path(tmp_file.name)
