from telegrambot_receiver_service.services.receiver import WebhookReceiver
from telegrambot_receiver_service.services.telegram import teardown_webhook
from telegrambot_receiver_service.settings import redis_settings
from telegrambot_receiver_service.utils import async_gather


def run():
    publishers = list()
    if redis_settings.enabled:
        from telegrambot_receiver_service.services.publishers.redis import RedisPublisher
        publishers.append(RedisPublisher())

    async_gather(*[publisher.connect() for publisher in publishers])

    try:
        receiver = WebhookReceiver(publishers)
        receiver.run()

    finally:
        async_gather(*[publisher.close() for publisher in publishers], teardown_webhook())
