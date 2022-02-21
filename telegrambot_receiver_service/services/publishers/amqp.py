from typing import Optional

import aio_pika

from telegrambot_receiver_service.services.publishers.base import BasePublisher
from telegrambot_receiver_service.settings import amqp_settings
from telegrambot_receiver_service.logging import logger


class AMQPPublisher(BasePublisher):
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.Channel]
    _exchange: Optional[aio_pika.Exchange]

    def __init__(self):
        self._connection = None
        self._channel = None

    async def connect(self):
        logger.info("Connecting AMQP....")

        logger.debug("Creating AMQP connection...")
        self._connection = await aio_pika.connect_robust(url=amqp_settings.url)

        logger.debug("Creating AMQP channel...")
        self._channel = await self._connection.channel()

        logger.debug("Getting AMQP exchange...")
        self._exchange = await self._channel.get_exchange(amqp_settings.exchange, ensure=False)

        logger.info("AMQP connected")
        return self

    async def close(self):
        if self._channel and not self._channel.is_closed:
            logger.debug("Closing AMQP channel...")
            await self._channel.close()
            logger.info("AMQP channel closed")
        else:
            logger.debug("No need to close AMQP channel")

        if self._connection and not self._connection.is_closed:
            logger.debug("Closing AMQP connection")
            await self._connection.close()
            logger.info("AMQP connection closed")
        else:
            logger.debug("No need to close AMQP connection")

        self._exchange, self._connection, self._channel = None, None, None

    async def publish(self, data: bytes):
        logger.debug("Enqueuing data into AMQP...")
        message = aio_pika.Message(body=data)
        if amqp_settings.deliverymode_persistent:
            message.delivery_mode = aio_pika.DeliveryMode(2)

        await self._exchange.publish(
            message=message,
            routing_key=amqp_settings.routingkey
        )
        logger.debug("AMQP data enqueued")
