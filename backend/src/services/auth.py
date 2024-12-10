import functools

from fastapi.security import OAuth2PasswordBearer
from fastapi_keycloak import FastAPIKeycloak

from src.services.utils import find_nth_occurrence

# Доработка класса для использования в докер контейнере
class CustomKeycloakAPI(FastAPIKeycloak):

    def __init__(self,
            server_url: str,
            client_id: str,
            client_secret: str,
            realm: str,
            admin_client_secret: str,
            callback_uri: str,
            server_public_url: str | None = None,
            admin_client_id: str = "admin-cli",
            scope: str = "openid profile email",
            timeout: int = 10):
        # Получение аргументов функции
        kwargs = locals()
        kwargs.pop("server_public_url")
        kwargs.pop("self")
        kwargs.pop("__class__")

        super().__init__(**kwargs)
        if server_public_url is None:
            self.server_public_url = server_url
        else:
            self.server_public_url = server_public_url

    @functools.cached_property
    def user_auth_scheme(self) -> OAuth2PasswordBearer:
        """Returns the auth scheme to register the endpoints with swagger

        Returns:
            OAuth2PasswordBearer: Auth scheme for swagger
        """
        try:
            return OAuth2PasswordBearer(tokenUrl=self.server_public_url + self.token_uri[find_nth_occurrence(self.token_uri, '/', 3)+1:])
        except:
            return OAuth2PasswordBearer(tokenUrl=self.token_uri)