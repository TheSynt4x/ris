import asyncio
import json
import os
import time
from pathlib import Path

import websockets

from app import loader
from app.core import logger, settings


async def send(websocket, type, message):
    await websocket.send(json.dumps({"type": type, "message": json.dumps(message)}))


async def handler(websocket):
    async for message in websocket:
        # todo: implement handlers

        recv = json.loads(message)

        logger.info(recv)

        if "command" not in recv:
            raise Exception("command not in payload")

        # todo: add enums for each command
        if recv["command"] == "init":
            await send(websocket, "subreddits", settings.subreddits)
            await send(websocket, "categories", settings.categories)
            await send(websocket, "global_post_limit", settings.global_post_limit)
        elif recv["command"] == "get_content":
            images = []

            format = None
            if "format" in recv["params"]:
                format = recv["params"]["format"]

            for path in Path("assets").rglob("**/*"):
                if len(path.name.split(".")) == 1:
                    continue

                image_id, image_format = path.name.split(".")

                if format and format != image_format:
                    continue

                images.append(
                    {
                        "id": image_id,
                        "url": str(path.absolute()),
                        "format": image_format,
                        "modified_at": time.ctime(os.path.getmtime(path)),
                    }
                )

            if "limit" in recv["params"]:
                images = images[: recv["params"]["limit"]]

            await send(websocket, "submissions", images)


async def main():
    await loader.load_settings()

    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
