from dadata.asynchr import DadataClient

from src.config import dadata_config

class DadataParser:

    # Клиент для взаимодействия с API Dadata
    client: DadataClient = DadataClient(dadata_config.api_token)

    async def fulltext_country_search(self, country: str) -> list[dict]:
        return await self.client.suggest("currency", country)