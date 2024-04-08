from getpass import getpass
from pathlib import Path
from time import time
from typing import Optional
from urllib.parse import urljoin
from webbrowser import open_new_tab

from jwt import decode as jwt_decode
from pydantic import (
    HttpUrl,
    SecretStr,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import get, post

from galileo_core.constants.routes import Routes
from galileo_core.helpers.api_client import ApiClient
from galileo_core.helpers.logger import logger


class GalileoConfig(BaseSettings):
    console_url: HttpUrl

    # User auth details.
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    api_key: Optional[SecretStr] = None
    jwt_token: Optional[SecretStr] = None
    current_user: Optional[str] = None

    # Config file for this project.
    config_filename: str = "core-config.json"

    model_config = SettingsConfigDict(
        # Allow loading from environment variables.
        env_prefix="GALILEO_",
        # Ignore unknown fields when loading from a config file.
        extra="ignore",
        # Validate fields at assignment.
        validate_assignment=True,
    )

    @computed_field
    def api_url(self) -> Url:
        # Local dev.
        if self.console_url.host in ["localhost", "127.0.0.1"]:
            api_url = "http://localhost:8088"
        else:
            api_url = self.console_url.unicode_string().replace("console", "api")
        return Url(api_url)

    def get_token_from_ui(self) -> str:
        token_url = urljoin(str(self.console_url), Routes.get_token)
        logger.info(f"🔐 Opening {token_url} to generate a new token.")
        try:
            open_new_tab(token_url)
        except Exception:
            pass
        finally:
            print(f"Go to {token_url} to generate a new token.")
            return getpass("🔐 Enter your token:")

    def login(self) -> None:
        token_data = {}
        if self.api_key:
            logger.debug("Logging in with API key.")
            token_data = ApiClient.make_request(
                post,
                base_url=str(self.api_url),
                endpoint=Routes.api_key_login,
                json=dict(api_key=self.api_key.get_secret_value()),
            )
        elif self.username and self.password:
            logger.debug("Logging in with username and password.")
            token_data = ApiClient.make_request(
                post,
                base_url=str(self.api_url),
                endpoint=Routes.username_login,
                data=dict(username=self.username, password=self.password.get_secret_value(), auth_method="email"),
            )
        else:
            logger.debug("No credentials found. Attempting to log in with token.")

        if (jwt_token := token_data.get("access_token")) is None:
            logger.debug("No credentials found. Attempting to log in with token.")
            jwt_token = self.get_token_from_ui()
        self.jwt_token = SecretStr(jwt_token)
        logger.debug("Logged in successfully.")
        self.current_user = self.api_client.request(get, path=Routes.current_user).get("email")
        self.write()
        print(f"👋 You have logged into 🔭 Galileo ({self.console_url}) as {self.current_user}.")

    def refresh_jwt_token(self) -> None:
        """Refresh token if not present or expired."""
        # Check to see if our token is expired before making a request
        # and refresh token if it's expired
        if self.jwt_token:
            claims = jwt_decode(self.jwt_token.get_secret_value(), options={"verify_signature": False})
            if claims.get("exp", 0) < time():
                self.login()

    @property
    def config_file(self) -> Path:
        return Path.home().joinpath(".galileo", self.config_filename)

    @field_validator("console_url", mode="before")
    def http_url(cls, value: str) -> str:
        if value and not (value.startswith("https") or value.startswith("http")):
            value = f"https://{value}"
        return value

    @model_validator(mode="after")
    def validate_api_url(self) -> "GalileoConfig":
        ApiClient.make_request(get, base_url=str(self.api_url), endpoint=Routes.healthcheck)
        return self

    @field_serializer("password", "jwt_token", "api_key", when_used="json-unless-none")
    def serialize_secrets(self, value: SecretStr) -> str:
        return value.get_secret_value()

    def write(self) -> None:
        self.config_file.parent.mkdir(exist_ok=True)
        self.config_file.write_text(self.model_dump_json(exclude_none=True))

    @property
    def api_client(self) -> ApiClient:
        self.refresh_jwt_token()
        if not self.jwt_token:
            raise ValueError("No token set. Please log in.")
        return ApiClient(host=self.api_url, jwt_token=self.jwt_token)

    def reset(self) -> None:
        # Reset credentials.
        self.username = None
        self.password = None
        self.api_key = None
        self.jwt_token = None
        self.current_user = None

    def logout(self) -> None:
        self.reset()
        self.write()
        print(f"👋 You have logged out of 🔭 Galileo ({self.console_url}).")
