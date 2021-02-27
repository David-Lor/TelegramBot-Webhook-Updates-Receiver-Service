import abc
import asyncio
import json
from typing import Optional, List, Tuple

import sanic
import sanic.request
import sanic.response

from telegrambot_receiver_service.services.publishers.base import BasePublisher
from telegrambot_receiver_service.services.telegram import setup_webhook
from telegrambot_receiver_service.utils import get_uuid, ip_in_network
from telegrambot_receiver_service.settings import webhook_settings, telegram_settings
from telegrambot_receiver_service.logging import logger


class BaseReceiver(abc.ABC):
    @abc.abstractmethod
    async def publish(self, data: str):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class WebhookReceiver(BaseReceiver):
    def __init__(self, publishers: List[BasePublisher]):
        self.publishers = publishers

        if webhook_settings.endpoint_is_random:
            webhook_endpoint = get_uuid()
        elif webhook_settings.endpoint_is_telegram_token:
            webhook_endpoint = telegram_settings.token
        else:
            webhook_endpoint = webhook_settings.endpoint
        self.webhook_endpoint = webhook_endpoint
        logger.info(f"Telegram Webhook endpoint is {self.webhook_endpoint}")

        self._app = sanic.Sanic("TelegramBotReceiverService")
        self._app.add_route(self._endpoint_webhook, f"/{self.webhook_endpoint}", methods=["POST"])
        if webhook_settings.status_endpoint:
            self._app.add_route(self._endpoint_status, "/status", methods=["GET", "POST"])

    @staticmethod
    def get_response_ok():
        return sanic.response.raw(body="OK", content_type="text/plain")

    @staticmethod
    def get_response_bad_request(message: str = "Bad request"):
        return sanic.response.raw(body=message, content_type="text/plain", status=400)

    @staticmethod
    def get_response_forbidden(message: str = "Forbidden"):
        return sanic.response.raw(body=message, content_type="text/plain", status=403)

    @staticmethod
    def _validate_ip(request: sanic.request.Request) -> Tuple[bool, Optional[str]]:
        # TODO Try calling this without ngrok (opening port and accessing public IP)
        #  requst.remote_addr seems to be always None?
        ip = request.remote_addr or request.headers.get("x-forwarded-for")
        limit_subnetworks = webhook_settings.limit_subnetworks
        if not limit_subnetworks:
            return True, ip
        if not ip:
            return False, ip

        return any(ip_in_network(ip, subnet) for subnet in limit_subnetworks), ip

    async def _endpoint_status(self, request: sanic.request.Request):
        return self.get_response_ok()

    async def _endpoint_webhook(self, request: sanic.request.Request):
        allowed_ip, ip = self._validate_ip(request)
        if not allowed_ip:
            logger.debug(f"Received request from non-allowed IP {ip}")
            return self.get_response_forbidden()

        data = request.json
        logger.debug(f"Telegram Webhook received: {data}")

        if not isinstance(data, dict):
            return self.get_response_bad_request()

        # TODO Could access request body/data directly and not parse+stringify json
        # TODO Setting to publish without leaving request pending? (fire & forget)
        await self.publish(json.dumps(data))
        return self.get_response_ok()

    async def publish(self, data: str):
        await asyncio.gather(*[publisher.publish(data) for publisher in self.publishers])

    def run(self):
        webhook_url = f"https://{webhook_settings.domain}/{self.webhook_endpoint}"
        asyncio.run(setup_webhook(webhook_url))
        self._app.run(host=webhook_settings.bind, port=webhook_settings.port)
