from typing import Optional

import aioredis

from telegrambot_receiver_service.services.publishers.base import BasePublisher
from telegrambot_receiver_service.settings import redis_settings
from telegrambot_receiver_service.logging import logger


class RedisPublisher(BasePublisher):
    _redis: Optional[aioredis.Redis]

    def __init__(self):
        self._redis = None

    async def connect(self):
        logger.info("Connecting Redis...")
        self._redis = await aioredis.create_redis_pool(redis_settings.url)
        logger.info("Redis connected")
        return self

    async def close(self):
        if self._redis and not self._redis.closed:
            logger.debug("Closing Redis...")
            self._redis.close()
            # await self._redis.wait_closed()
            logger.info("Redis closed")
        self._redis = None

    async def publish(self, data: str):
        logger.debug(f"Enqueuing data into Redis: {data}")
        await self._redis.rpush(redis_settings.queue_name, data)
        logger.debug("Redis data enqueued")
