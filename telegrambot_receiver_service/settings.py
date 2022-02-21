import os
from typing import Optional, List

from netaddr import IPNetwork

import pydantic
from pydantic import constr

String = constr(strip_whitespace=True, min_length=1)
StringEmptiable = constr(strip_whitespace=True)

ENV_FILE = os.getenv("ENV_FILE", ".env")


class BaseSettings(pydantic.BaseSettings):
    class Config:
        env_file = ENV_FILE


class WebhookSettings(BaseSettings):
    domain: String
    endpoint: String = "random"
    bind: String = "0.0.0.0"
    port: int = 8000
    status_endpoint: bool = True
    publish_timeout: float = 5
    limit_subnets: Optional[String] = None  # example: "149.154.160.0/20, 91.108.4.0/22"

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
    token: String
    delete_webhook: bool = True
    api_url: String = "https://api.telegram.org"

    class Config(BaseSettings.Config):
        env_prefix = "TELEGRAM_"


class RedisSettings(BaseSettings):
    url: Optional[String] = None  # example: "redis://localhost:6379"
    queue_name: String = "telegram_bot"

    @property
    def enabled(self):
        return bool(self.url)

    class Config(BaseSettings.Config):
        env_prefix = "REDIS_"


class AMQPSettings(BaseSettings):
    url: Optional[String] = None  # example: amqp://user:pass@localhost:5672/vhost
    exchange: StringEmptiable = ""
    routingkey: StringEmptiable = ""
    deliverymode_persistent: bool = False

    @property
    def enabled(self):
        return bool(self.url)

    class Config(BaseSettings.Config):
        env_prefix = "AMQP_"


class GeneralSettings(BaseSettings):
    publisher_connect_timeout: float = 10
    teardown_timeout: float = 10
    log_level: String = "INFO"


webhook_settings = WebhookSettings()
telegram_settings = TelegramSettings()
redis_settings = RedisSettings()
amqp_settings = AMQPSettings()
general_settings = GeneralSettings()
