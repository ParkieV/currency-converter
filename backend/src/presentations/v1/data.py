import asyncio
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_keycloak import OIDCUser
from starlette.responses import StreamingResponse

from src.config import keycloak_openid
from src.logger import logger
from src.repositories.postgres import CurrenciesCRUD, PostgresContext
from src.services.currencies import (convert_currencies, draw_dynamics_graphic,
                                     get_currency_dynamics)
from src.services.parsers import Parser
from src.services.utils import read_file_by_chunks

router = APIRouter()


@router.get("/rates", description="Конвертировать валюту")
async def get_rates(
    symbol_from: str = Query(..., alias="from"),
    symbol_to: str = Query(..., alias="to"),
    value: float = Query(1.0),
    user: OIDCUser = Depends(keycloak_openid.get_current_user()),
) -> dict[str, float]:
    """Эндпоинт для конвертации валюты"""
    try:
        return {"result": await convert_currencies(symbol_from, symbol_to, value)}
    except ValueError as e:
        if "Can't convert" in str(e) and "base" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Base currency symbol is incorrect",
            )
        elif "Can't convert" in str(e) and "target" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target currency symbol is incorrect",
            )


@router.get("/get-current-exchange-rate")
async def get_current_exchange_rate(
    user: OIDCUser = Depends(keycloak_openid.get_current_user()),
) -> list[CurrenciesCRUD]:
    """Эндпоинт для получения курса валют на сегодня от ЦБ"""
    db_context = PostgresContext(crud=CurrenciesCRUD())
    result = []
    async with db_context.new_session() as session:
        result = await db_context.crud.get_exchange_rates(date.today(), session)

    if len(result) > 0:
        return result

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No currencies data found for {date.today()}",
    )


@router.get("/get-currency-dynamics")
async def get_dynamics(
    date_start: str = Query(...),
    date_end: str = Query(...),
    curr_symbol: str = Query(...),
    user: OIDCUser = Depends(keycloak_openid.get_current_user()),
) -> StreamingResponse:
    """Эндпоинт для получения графика изменения валюты в указанный промежуток"""
    try:
        date_start = datetime.strptime(date_start, "%d/%m/%Y").date()
    except Exception as e:
        logger.error(
            f"Failed to parse end date {date_end}. {e.__class__.__name__}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect start date format",
        )

    try:
        date_end = datetime.strptime(date_end, "%d/%m/%Y").date()
    except Exception as e:
        logger.error(
            f"Failed to parse end date {date_end}. {e.__class__.__name__}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect end date format"
        )

    if date_start >= date_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect dates"
        )

    dynamics_data = await get_currency_dynamics(curr_symbol, date_start, date_end)

    tmpfile_path = await asyncio.to_thread(draw_dynamics_graphic, dynamics_data)

    return StreamingResponse(read_file_by_chunks(tmpfile_path), media_type="image/png")


@router.get("/search-country-currency-info")
async def get_country_currency_info(
    country: str = Query(...),
    user: OIDCUser = Depends(keycloak_openid.get_current_user()),
) -> list[dict]:
    """Поиск информации о валюте по стране"""
    parser = Parser()
    return await parser.get_gov_currency_data(country)
