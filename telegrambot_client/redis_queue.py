import redis

from .logging import logger


class RedisQueue:
    def __init__(self, url, queue_name):
        self._redis = redis.from_url(url)
        self._queue_name = queue_name
        logger.info("Redis instance initialized")

    def get(self):
        """Retrieve an object from the queue, as string"""
        data = self._redis.blpop(self._queue_name)[1]
        try:
            data = data.decode()
            logger.bind(read_data=data).debug("Read from Redis queue")
            return data
        except AttributeError:
            logger.bind(read_data=data).warning("Invalid data received in Redis queue")
