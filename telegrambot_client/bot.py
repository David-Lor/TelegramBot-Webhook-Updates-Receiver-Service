from uuid import uuid4

import telebot
import telebot.types

from .bot_handlers import register_handlers
from .redis_queue import RedisQueue
from .logging import logger


class Bot:
    def __init__(self, token: str, redis_queue: RedisQueue):
        self._bot = telebot.TeleBot(token)
        register_handlers(self._bot)
        self._redis_queue = redis_queue

    def _handle_update(self, data: str):
        with logger.contextualize(request_id=str(uuid4())):
            # noinspection PyBroadException
            try:
                logger.bind(update_data=data).info("Received update")
                update_object = telebot.types.Update.de_json(data)
                logger.debug("Update parsed successfully")
                self._bot.process_new_updates([update_object])

            except Exception:
                logger.exception("Error processing update")

    def run(self):
        logger.info("Bot start running")

        while True:
            try:
                update = self._redis_queue.get()
                self._handle_update(update)

            except (KeyboardInterrupt, InterruptedError):
                break

        logger.info("Bot stopped running")
