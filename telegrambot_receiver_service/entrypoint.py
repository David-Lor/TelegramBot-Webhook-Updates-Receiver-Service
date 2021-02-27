import asyncio

from telegrambot_receiver_service.services.receiver import WebhookReceiver
from telegrambot_receiver_service.services.publisher import RedisPublisher
from telegrambot_receiver_service.services.telegram import teardown_webhook
from telegrambot_receiver_service.settings import redis_settings
from telegrambot_receiver_service.utils import async_gather


# async def _run():
#     publishers = list()
#     if redis_settings.enabled:
#         publishers.append(RedisPublisher())
#
#     await asyncio.gather(*[publisher.connect() for publisher in publishers])
#
#     try:
#         receiver = WebhookReceiver(publishers)
#         await receiver.run()
#
#     finally:
#         await asyncio.gather(*[publisher.close() for publisher in publishers], teardown_webhook())


# def run():
#     asyncio.run(_run())


def run():
    publishers = list()
    if redis_settings.enabled:
        publishers.append(RedisPublisher())

    # asyncio.get_event_loop().run_until_complete(
    #     asyncio.gather(*[publisher.connect() for publisher in publishers])
    # )
    async_gather(*[publisher.connect() for publisher in publishers])

    try:
        receiver = WebhookReceiver(publishers)
        receiver.run()

    finally:
        async_gather(*[publisher.close() for publisher in publishers], teardown_webhook())
