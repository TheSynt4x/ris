import asyncio
import json

import pymysql
import websockets

from app import libs, loader
from app.core import logger, settings


from pathlib import Path


async def send(websocket, type, message):
    await websocket.send(json.dumps({"type": type, "message": json.dumps(message)}))


async def handler(websocket):
    async for message in websocket:
        # todo: implement handlers

        if message == "init":
            logger.info(f"sending settings: {settings.subreddits}")
            await send(websocket, "subreddits", settings.subreddits)
            await send(websocket, "categories", settings.categories)
            await send(websocket, "global_post_limit", settings.global_post_limit)

        elif message == "get_content":
            if settings.db_conn:
                # todo: implement message arguments, so message can send limit={x}
                images = await libs.db.get(
                    "submissions", limit=392, cursor_cls=pymysql.cursors.DictCursor
                )
            else:
                images = []

                # todo: move to utils, implement limit={x} logic
                for path in Path("assets").rglob("*"):
                    images.append({"url": str(path.absolute())})

            await send(websocket, "submissions", images)

        elif message == "add_subreddit":
            pass

        elif message == "add_category":
            pass

        elif message == "run":
            pass


async def main():
    await loader.load_settings()

    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
