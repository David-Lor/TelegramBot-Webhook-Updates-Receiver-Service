import asyncio

import uvloop

from telegrambot_receiver_service.services.receivers.webhook import WebhookReceiver
from telegrambot_receiver_service.services.telegram import teardown_webhook
from telegrambot_receiver_service.settings import redis_settings, amqp_settings, general_settings
from telegrambot_receiver_service.utils import async_gather


def run():
    asyncio.set_event_loop(uvloop.new_event_loop())

    publishers = list()
    if redis_settings.enabled:
        from telegrambot_receiver_service.services.publishers.redis import RedisPublisher
        publishers.append(RedisPublisher())
    if amqp_settings.enabled:
        from telegrambot_receiver_service.services.publishers.amqp import AMQPPublisher
        publishers.append(AMQPPublisher())

    async_gather(*[publisher.connect() for publisher in publishers],
                 timeout=general_settings.publisher_connect_timeout)

    try:
        receiver = WebhookReceiver(publishers)
        receiver.run()

    finally:
        async_gather(*[publisher.close() for publisher in publishers], teardown_webhook(),
                     timeout=general_settings.teardown_timeout)
