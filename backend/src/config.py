from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import logger


class DBConfig(BaseSettings):
    driver: str
    host: str
    port: int | None = Field(default=None)
    username: str
    password: str
    db_name: str = Field(validation_alias="db_name")

    @property
    def db_url(self):
        db_url = f"{self.driver}://{self.username}:{self.password}@{self.host}{f':{self.port}' if self.port else ''}/{self.db_name}"
        logger.debug("DB URL: %s", db_url)
        return db_url

    model_config = SettingsConfigDict(env_prefix="DB_", extra="allow")


class DadataConfig(BaseSettings):
    """Конфигурация для API Dadata"""

    api_token: str

    model_config = SettingsConfigDict(env_prefix="DADATA_", extra="allow")

db_config = DBConfig()
dadata_config = DadataConfig()
