import urllib.parse
from typing import Optional

import httpx

from telegrambot_receiver_service.settings import telegram_settings
from telegrambot_receiver_service.logging import logger


async def _request(endpoint: str, body: Optional[dict]):
    async with httpx.AsyncClient() as client:
        logger.debug(f"Calling Telegram bot API endpoint {endpoint}...")
        url = urllib.parse.urljoin(telegram_settings.api_url, f"/bot{telegram_settings.token}/{endpoint}")

        response = await client.post(url, json=body)
        logger.debug(f"Telegram bot API call to {endpoint} returned {response.status_code} {response.text}")
        response.raise_for_status()
        return response


async def setup_webhook(url: str):
    logger.info(f"Asking Telegram to setup webhook (url={url})...")
    data = dict(url=url, max_connections=100)
    await _request(endpoint="setWebhook", body=data)
    logger.info("Telegram webhook set")


async def teardown_webhook():
    logger.info("Asking Telegram to delete webhook...")
    await _request(endpoint="deleteWebhook", body=None)
    logger.info("Telegram webhook deleted")
