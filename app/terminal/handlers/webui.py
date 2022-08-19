import os
import subprocess
import sys
import threading

from app.core import logger


class WebUI:
    name = "webui"

    async def handle(self, *args):
        def run_server():
            logger.info("starting server...")

            return subprocess.run(
                [sys.executable, "server.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

        def run_client():
            logger.info("starting client...")
            os.system("start ./webui/index.html")

        server = threading.Thread(target=run_server)
        server.start()

        client = threading.Thread(target=run_client)
        client.start()
