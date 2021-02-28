import asyncio
import json
from signal import signal, SIGINT
from typing import Optional, List, Tuple

import sanic
import sanic.request
import sanic.response

from telegrambot_receiver_service.services.publishers.base import BasePublisher
from telegrambot_receiver_service.services.telegram import setup_webhook
from telegrambot_receiver_service.services.receivers.base import BaseReceiver
from telegrambot_receiver_service.utils import get_uuid, ip_in_network
from telegrambot_receiver_service.settings import webhook_settings, telegram_settings
from telegrambot_receiver_service.logging import logger


class WebhookReceiver(BaseReceiver):
    def __init__(self, publishers: List[BasePublisher]):
        super().__init__(publishers)

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
    def _get_plain_response(body: str, status: int):
        return sanic.response.raw(body=body, content_type="text/plain", status=status)

    @classmethod
    def get_response_ok(cls, message: str = "OK"):
        return cls._get_plain_response(body=message, status=200)

    @classmethod
    def get_response_bad_request(cls, message: str = "Bad request"):
        return cls._get_plain_response(body=message, status=400)

    @classmethod
    def get_response_forbidden(cls, message: str = "Forbidden"):
        return cls._get_plain_response(body=message, status=403)

    @classmethod
    def get_response_internal_error(cls, message: str = "Internal server error"):
        return cls._get_plain_response(body=message, status=500)

    @staticmethod
    def _validate_ip(request: sanic.request.Request) -> Tuple[bool, Optional[str]]:
        # TODO Try calling this without ngrok (opening port and accessing public IP)
        ip = request.headers.get("x-forwarded-for") or request.remote_addr or request.ip
        limit_subnetworks = webhook_settings.limit_subnetworks
        if not limit_subnetworks:
            return True, ip
        if not ip:
            return False, ip

        return any(ip_in_network(ip, subnet) for subnet in limit_subnetworks), ip

    async def _endpoint_status(self, request: sanic.request.Request):
        return self.get_response_ok()

    async def _endpoint_webhook(self, request: sanic.request.Request):
        with logger.contextualize(request_id=get_uuid()):
            # noinspection PyBroadException
            try:
                ip_is_allowed, ip = self._validate_ip(request)
                if not ip_is_allowed:
                    logger.debug(f"Received request from non-allowed IP {ip}")
                    return self.get_response_forbidden()

                data = request.json
                logger.bind(webhook_received_data=data).debug("Telegram Webhook received")

                if not isinstance(data, dict):
                    return self.get_response_bad_request()

                # TODO Could access request body/data directly and not parse+stringify json
                # TODO Setting to publish without leaving request pending? (fire & forget)
                await asyncio.wait_for(self.publish(json.dumps(data)), timeout=webhook_settings.publish_timeout)
                return self.get_response_ok()

            except Exception:
                logger.exception("Error handling webhook request")
                return self.get_response_internal_error()

    async def publish(self, data: str):
        await asyncio.gather(*[publisher.publish(data) for publisher in self.publishers])

    def run(self):
        # https://github.com/sanic-org/sanic/blob/master/examples/run_async.py
        loop = asyncio.get_event_loop()

        # TODO run task in entrypoint, gather with publisher.connect() calls
        webhook_url = f"https://{webhook_settings.domain}/{self.webhook_endpoint}"
        loop.run_until_complete(setup_webhook(webhook_url))

        server = self._app.create_server(host=webhook_settings.bind, port=webhook_settings.port,
                                         return_asyncio_server=True)

        asyncio.ensure_future(server, loop=loop)
        signal(SIGINT, lambda s, f: loop.stop())

        # noinspection PyBroadException
        try:
            loop.run_forever()
        except:
            loop.stop()
