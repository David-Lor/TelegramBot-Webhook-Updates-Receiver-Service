import os

import pydantic

ENV_FILE = os.getenv("ENV_FILE", ".env")


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class TelegramSettings(BaseSettings):
    token: str

    class Config(BaseSettings.Config):
        env_prefix = "TELEGRAM_"


class RedisSettings(BaseSettings):
    url: pydantic.RedisDsn = "redis://localhost:6379"
    queue_name: str = "telegram_bot"

    class Config(BaseSettings.Config):
        env_prefix = "REDIS_"


class GeneralSettings(BaseSettings):
    log_level: str = "DEBUG"
