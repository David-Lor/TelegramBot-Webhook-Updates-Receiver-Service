from .bot import Bot
from .redis_queue import RedisQueue
from .settings import TelegramSettings, RedisSettings


def run():
    telegram_settings = TelegramSettings()
    redis_settings = RedisSettings()

    redis_queue = RedisQueue(url=redis_settings.url, queue_name=redis_settings.queue_name)
    bot = Bot(token=telegram_settings.token, redis_queue=redis_queue)
    bot.run()
