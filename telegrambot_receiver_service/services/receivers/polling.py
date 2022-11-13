import asyncio
from typing import List, Optional

from telegrambot_receiver_service.services.publishers.base import BasePublisher
from telegrambot_receiver_service.services.receivers.base import BaseReceiver
from telegrambot_receiver_service.services.telegram import get_updates
from telegrambot_receiver_service.logging import logger


class PollingReceiver(BaseReceiver):

    def __init__(self, publishers: List[BasePublisher]):
        super().__init__(publishers)

        self._last_update_id = None

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.async_run())

    async def async_run(self):
        logger.info("Start of Telegram getUpdates loop")

        while True:
            try:
                updates_data = await self._polling_get_updates()
                asyncio.create_task(self.publish_multiple(updates_data))

            except (KeyboardInterrupt, InterruptedError):
                break

        logger.info("Telegram getUpdates loop stopped")

    async def _polling_get_updates(self) -> List[str]:
        offset = self._get_last_update_offset()
        result = await get_updates(offset=offset)
        if result.last_update_id is not None:
            self._last_update_id = result.last_update_id

        return [update.data for update in result.updates]

    def _get_last_update_offset(self) -> Optional[int]:
        if self._last_update_id is not None:
            return self._last_update_id + 1
        return None
