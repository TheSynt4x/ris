import subprocess
import sys
import threading

from app.core import logger


class WebUI:
    name = "webui"

    async def handle(self, *args):
        def run():
            logger.info("starting server...")

            return subprocess.run(
                [sys.executable, "server.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

        thread = threading.Thread(target=run)
        thread.start()
