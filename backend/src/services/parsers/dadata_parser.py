from typing import Any

from dadata.asynchr import DadataClient

from src.config import dadata_config


class DadataParser:
    """Класс для парсинга данных через DaData API"""

    # Клиент для взаимодействия с API Dadata
    client: DadataClient = DadataClient(dadata_config.api_token)

    async def fulltext_currency_search(self, country: str) -> list[dict[str, Any]]:
        """
        Метод для получения данных о государственной валюте страны через API DaData
        :param country: Страна
        :return: Данные о валюте
        """

        return await self.client.suggest("currency", country)
