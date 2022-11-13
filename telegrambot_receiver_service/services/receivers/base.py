import abc
import asyncio
from typing import List

from telegrambot_receiver_service.services.publishers.base import BasePublisher


class BaseReceiver(abc.ABC):
    publishers: List[BasePublisher]

    def __init__(self, publishers: List[BasePublisher]):
        self.publishers = publishers

    async def publish_multiple(self, datas: List[str]):
        await asyncio.gather(*[self.publish(data) for data in datas])

    async def publish(self, data: str):
        await asyncio.gather(*[publisher.publish(data) for publisher in self.publishers])

    @abc.abstractmethod
    def run(self):
        pass
