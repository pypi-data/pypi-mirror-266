import configparser
import os
import time
from pathlib import Path

from appdirs import user_config_dir

from .auth import authenticate_keycloak


class Config:  # pylint: disable=too-many-instance-attributes
    config_path: Path = Path()
    service_url: str = "https://functions.cs-0b.contact-cloud.com"
    _conf: configparser.ConfigParser | None = None
    _client_id: str = ""
    _client_secret: str = ""
    _access_token: str = ""
    token_valid_until: int = 0

    def __init__(self, config_directory=None):
        self._conf = configparser.ConfigParser()

        self._ensure_config(config_directory)
        # set defaults and then try to load config from file
        self._set_conf()
        self._load()

    def _ensure_config(self, config_directory: str | None = None):
        """
        make sure that CONFIG_PATH is set to some config.ini that exists
        """
        if config_directory:
            config_directory = Path(config_directory)
        else:
            config_directory = Path(user_config_dir("cfc", "contact"))

        if not config_directory.exists():
            config_directory.mkdir(parents=True)
        self.config_path = Path(os.path.join(config_directory, "config.ini"))

    @property
    def access_token(self):
        """
        Fetches a valid access token.
        Access token is cached in the config file.
        :return:
        """
        if not self._access_token or float(self.token_valid_until) < time.time() + 5:
            self.refresh_token()
        return self._access_token

    def refresh_token(self):
        token, valid_until = authenticate_keycloak(self.client_id, self.client_secret)
        self._access_token = token
        self.token_valid_until = valid_until
        self.save()

    @property
    def client_id(self):
        if self._client_id == "":
            raise ValueError("client ID not set")
        return self._client_id

    @client_id.setter
    def client_id(self, client_id: str):
        self._client_id = client_id

    @property
    def client_secret(self):
        if self._client_secret == "":  # nosec
            raise ValueError("client secret not set")
        return self._client_secret

    @client_secret.setter
    def client_secret(self, client_secret: str):
        self._client_secret = client_secret

    def _set_conf(self):
        self._conf["default"] = {
            "service_url": self.service_url,
            "_access_token": self._access_token,
            "token_valid_until": self.token_valid_until,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

    def _load(self):
        """will try to load from environment variables first, then from config file, then loads defaults"""
        self._conf.read(self.config_path)

        self.service_url = os.getenv("CFC_SERVICE_URL") or self._conf.get(
            "default", "service_url", fallback=self.service_url
        )
        self._access_token = os.getenv("CFC_TOKEN") or self._conf.get(
            "default", "_access_token", fallback=self._access_token
        )
        self._client_id = self._conf.get("default", "client_id", fallback="")
        self._client_secret = self._conf.get("default", "client_secret", fallback="")
        self.token_valid_until = self._conf.get(
            "default", "token_valid_until", fallback=0
        )

    def save(self):
        self._set_conf()
        with open(self.config_path, "w", encoding="utf-8") as f:
            self._conf.write(f)


config = Config()
