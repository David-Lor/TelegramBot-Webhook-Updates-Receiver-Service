import abc
from typing import List

from telegrambot_receiver_service.services.publishers.base import BasePublisher


class BaseReceiver(abc.ABC):
    publishers: List[BasePublisher]

    def __init__(self, publishers: List[BasePublisher]):
        self.publishers = publishers

    @abc.abstractmethod
    async def publish(self, data: bytes):
        pass

    @abc.abstractmethod
    def run(self):
        pass
