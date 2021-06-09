import asyncio
import json
from typing import Dict, List
from typing_extensions import Final

from aiohttp import web, ClientSession, WSMsgType, WSMessage

from service import Components


BULK_SIZE: Final[int] = 1000
DEFAULT_COUNTRY: Final[str] = "USA"


async def ws_consumer(app: web.Application) -> None:
    ws_session: ClientSession = app["ws_session"]
    url: str = app["websocket_addr"]
    components_service: Components = app["components_service"]
    messages: List[Dict[str, str]] = []
    try:
        async with ws_session.ws_connect(url) as ws:
            async for msg in ws:  # type: WSMessage
                if msg.type == WSMsgType.TEXT:
                    try:
                        data: Dict[str, str] = json.loads(msg.data)
                    except ValueError:
                        continue

                    if not isinstance(data, dict):
                        continue

                    if not data["country"]:
                        data["country"] = DEFAULT_COUNTRY

                    if len(messages) < BULK_SIZE:
                        messages.append(data)
                        continue

                    await components_service.insert_bulk(messages)
                    messages = []

                elif msg.type == WSMsgType.ERROR:
                    break
    except asyncio.CancelledError:
        if messages:
            # in case the list of messages was not cleaned, replace them
            await components_service.insert_bulk(messages, upsert=True)
