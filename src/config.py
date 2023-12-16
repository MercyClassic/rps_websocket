import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ConfigParseError(ValueError):
    pass


@dataclass
class Config:
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str


def get_str_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        logger.error(f'{key} is not set')
        raise ConfigParseError(f'{key} is not set')
    return value


def load_config():
    return Config(
        JWT_ACCESS_SECRET_KEY=get_str_env('JWT_ACCESS_SECRET_KEY'),
        JWT_REFRESH_SECRET_KEY=get_str_env('JWT_REFRESH_SECRET_KEY'),
        ALGORITHM=get_str_env('ALGORITHM'),
    )
