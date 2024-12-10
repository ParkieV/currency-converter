import functools

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import logger
from src.services.auth import CustomKeycloakAPI


class DBConfig(BaseSettings):
    driver: str
    host: str
    port: int | None = Field(default=None)
    username: str
    password: str
    db_name: str = Field(validation_alias="db_name")

    @functools.cached_property
    def db_url(self):
        db_url = f"{self.driver}://{self.username}:{self.password}@{self.host}{f':{self.port}' if self.port else ''}/{self.db_name}"
        return db_url

    model_config = SettingsConfigDict(env_prefix="DB_", extra="allow")


class DadataConfig(BaseSettings):
    """Конфигурация для API Dadata"""

    api_token: str

    model_config = SettingsConfigDict(env_prefix="DADATA_", extra="allow")


class KeycloakConfig(BaseSettings):
    server_url: str = Field(validation_alias='keycloak_uri')
    server_public_url: str | None = Field(validation_alias='keycloak_public_uri', default=None)
    client_id: str
    client_secret: str
    admin_secret: str
    realm_name: str
    callback_url: str = Field(validation_alias="backend_uri")
    admin_id: str = Field(default="admin-cli")

    model_config = SettingsConfigDict(env_prefix="KEYCLOAK_", extra="allow")


db_config = DBConfig()
dadata_config = DadataConfig()
keycloak_config = KeycloakConfig()
keycloak_openid = CustomKeycloakAPI(
    server_url=keycloak_config.server_url,
    client_id=keycloak_config.client_id,
    client_secret=keycloak_config.client_secret,
    admin_client_id=keycloak_config.admin_id,
    admin_client_secret=keycloak_config.admin_secret,
    realm=keycloak_config.realm_name,
    callback_uri=keycloak_config.callback_url,
    server_public_url=keycloak_config.server_public_url,
)
logger.info("Loading project configuration has successful!")