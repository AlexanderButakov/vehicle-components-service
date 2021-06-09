import asyncio
import logging
import os
import sys

from aiohttp import web, ClientSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from handler import get_data
from service import Components
from ws_background import ws_consumer


async def init_db(app: web.Application, address: str) -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(address)
    app["db_client"] = client
    db = client.components
    return db


async def close_db_client(app: web.Application) -> None:
    db_client: AsyncIOMotorClient = app["db_client"]
    db_client.close()


async def start_background_task(app: web.Application) -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(ws_consumer(app))


async def stop_background_task(app: web.Application) -> None:
    ws_session: ClientSession = app["ws_session"]
    if not ws_session.closed:
        await ws_session.close()


def main() -> None:
    try:
        websocket_addr = os.environ["WEBSOCKET_ADDR"]
        database_addr = os.environ["DATABASE_ADDR"]
    except KeyError as exc:
        logging.critical(str(exc))
        sys.exit(2)

    loop = asyncio.get_event_loop()

    app = web.Application()

    ws_session = ClientSession()
    app["ws_session"] = ws_session
    app["websocket_addr"] = websocket_addr

    db = loop.run_until_complete(init_db(app, database_addr))
    app["components_service"] = Components(db)

    app.add_routes([web.get("/data", get_data)])

    app.on_startup.append(start_background_task)
    app.on_shutdown.extend([close_db_client, stop_background_task])

    web.run_app(app)


if __name__ == '__main__':
    main()
