import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Literal

import aiofiles
from aiohttp import ClientSession

from src.logger import logger


async def fetch_url(
    url: str,
    session: ClientSession,
    method: Literal["GET", "POST", "DELETE", "PUT"] = "GET",
    headers: dict | None = None,
    queries: dict | None = None,
    return_json: bool = False,
    **kwargs,
):
    """
    Метод для получения данных с сайта

    :param url: URL сайта
    :param session: сессия, в рамках которой происходит запрос
    :param method: метод HTTP-запроса
    :param headers: заголовки запроса
    :param queries: query-параметры запроса
    :param return_json: необходимость возвращать результат в виде JSON

    :return: тело запроса, если запрос вернулся со статусом 200
    """
    match method:
        case "GET":
            async with session.get(
                url, headers=headers, params=queries, ssl=False, **kwargs
            ) as resp:
                if resp.status == 404:
                    raise ValueError("URL is not found")

                if resp.status != 200:
                    raise ValueError("Could not load URL")

                if return_json:
                    return await resp.json()
                return await resp.text()

        case "POST":
            async with session.post(
                url, headers=headers, params=queries, **kwargs
            ) as resp:
                if resp.status != 404:
                    raise ValueError("URL is not found")

                if return_json:
                    return await resp.json()
                return await resp.text()

        case _:
            raise ValueError("Invalid method")


async def read_file_by_chunks(
    file_path: Path, chunk_size: int = 1024 * 1024
) -> AsyncGenerator[bytes, None]:
    """
    Метод для чтения файла по чанкам

    :param file_path: путь до файла
    :param chunk_size: размер чанка

    :return: Чанк данных
    """
    try:
        async with aiofiles.open(file_path, mode="rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        logger.error(f"Failed to read file {file_path}. {e.__class__.__name__}: {e}")
        raise
    finally:
        os.remove(file_path)


def find_nth_occurrence(text, char, n):
    """
    Метод для возврата индекса искомого символа в строке по его номеру повтора

    :param text: текст
    :param char: символ для поиска
    :param n: номер повтора

    :return: индекс искомого символа
    """
    index = -1
    for _ in range(n):
        index = text.find(char, index + 1)
        if index == -1:
            return ValueError(f"Symbol '{char}' not found")
    return index
