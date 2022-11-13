import abc


class BasePublisher(abc.ABC):

    @abc.abstractmethod
    async def connect(self):
        pass

    @abc.abstractmethod
    async def close(self):
        pass

    @abc.abstractmethod
    async def publish(self, data: bytes):
        # TODO Fix typing for "bytes" (depending on the publisher, may use bytes or str)
        pass
