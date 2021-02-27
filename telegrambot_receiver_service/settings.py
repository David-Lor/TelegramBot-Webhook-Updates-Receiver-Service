import os
from typing import Optional, List

from netaddr import IPNetwork

import pydantic

ENV_FILE = os.getenv("ENV_FILE", ".env")


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class WebhookSettings(BaseSettings):
    domain: str
    endpoint: str = "random"
    bind: str = "0.0.0.0"
    port: int = 8000
    status_endpoint: bool = True
    limit_subnets: Optional[str] = None  # example: "149.154.160.0/20, 91.108.4.0/22"

    class Config(BaseSettings.Config):
        env_prefix = "WEBHOOK_"

    @property
    def endpoint_is_random(self):
        return self.endpoint == "random"

    @property
    def endpoint_is_telegram_token(self):
        return self.endpoint == "token"

    @property
    def limit_subnetworks(self) -> Optional[List[IPNetwork]]:
        # TODO Lazy loading?
        if not self.limit_subnets:
            return None
        subnets = self.limit_subnets.split(",")
        return [IPNetwork(subnet.strip()) for subnet in subnets]


class TelegramSettings(BaseSettings):
    token: str
    delete_webhook: bool = True

    class Config(BaseSettings.Config):
        env_prefix = "TELEGRAM_"


class RedisSettings(BaseSettings):
    url: Optional[str] = None  # example: "redis://localhost:6379"
    queue_name: str = "TelegramBotQueue"

    @property
    def enabled(self):
        return bool(self.url)

    class Config(BaseSettings.Config):
        env_prefix = "REDIS_"


class GeneralSettings(BaseSettings):
    log_level: str = "INFO"


webhook_settings = WebhookSettings()
telegram_settings = TelegramSettings()
redis_settings = RedisSettings()
general_settings = GeneralSettings()
