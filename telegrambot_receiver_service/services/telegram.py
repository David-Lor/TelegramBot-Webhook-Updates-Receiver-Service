import json
import urllib.parse
from typing import Optional, List

import httpx
import pydantic

from telegrambot_receiver_service.settings import telegram_settings
from telegrambot_receiver_service.logging import logger


async def _request(endpoint: str, body: Optional[dict], timeout: Optional[int] = None):
    client_kwargs = dict()
    if timeout is not None:
        client_kwargs["timeout"] = timeout

    async with httpx.AsyncClient(**client_kwargs) as client:
        logger.debug(f"Calling Telegram bot API endpoint {endpoint}...")
        url = urllib.parse.urljoin(telegram_settings.api_url, f"/bot{telegram_settings.token}/{endpoint}")

        response = await client.post(url, json=body)
        response.raise_for_status()
        logger.debug(f"Telegram bot API call to {endpoint} returned {response.status_code} {response.text}")
        return response


async def setup_webhook(url: str):
    logger.info("Asking Telegram to setup webhook...")
    data = dict(url=url, max_connections=100)
    await _request(endpoint="setWebhook", body=data)
    logger.info("Telegram webhook set")


async def teardown_webhook():
    logger.info("Asking Telegram to delete webhook...")
    await _request(endpoint="deleteWebhook", body=None)
    logger.info("Telegram webhook deleted")


class GetUpdatesResponse(pydantic.BaseModel):

    class Update(pydantic.BaseModel):
        data: str
        update_id: int

    updates: List[Update]
    last_update_id: Optional[int] = None


async def get_updates(offset: Optional[int]) -> GetUpdatesResponse:
    # TODO make func a generator to reuse the httpx.AsyncClient

    logger.debug("Telegram getUpdates...")
    timeout = telegram_settings.polling_timeout
    body = dict(
        timeout=timeout,
        offset=offset,
    )

    r = await _request(endpoint="getUpdates", body=body, timeout=timeout*1.5)
    r.raise_for_status()

    js = r.json()
    if not js.get("ok"):
        raise ValueError("Telegram getUpdates response is not valid")

    js = js.get("result", [])
    if not isinstance(js, list):
        raise ValueError("Telegram getUpdates response is not a JSON array")

    updates = list()
    updates_ids = list()
    for update_js in js:
        update = GetUpdatesResponse.Update(
            data=json.dumps(update_js),
            update_id=update_js["update_id"],
        )
        updates.append(update)
        updates_ids.append(update.update_id)

    result = GetUpdatesResponse(
        updates=updates,
        last_update_id=max(updates_ids) if updates_ids else None,
    )

    logger.debug("Telegram getUpdates OK")
    return result
