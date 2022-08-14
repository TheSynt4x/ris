import os
import sys

from aioconsole import ainput, aprint

from app.core import logger
from app.terminal import handlers


class Terminal:
    prompt = "ris> "

    handlers = [
        handlers.Run(),
        handlers.Config(),
        handlers.WebUI(),
        handlers.Mega(),
    ]

    async def start(self):
        while True:
            cmd = await ainput(self.prompt)

            args = cmd.split(" ")

            if args[0] == "help":
                for handler in self.handlers:
                    if not handler.handle.__doc__:
                        continue

                    await aprint(handler.handle.__doc__)

            elif args[0] == "exit":
                logger.info("exiting")

                try:
                    sys.exit(0)
                except Exception:
                    os._exit(0)

            for handler in self.handlers:
                if args[0].lower() == handler.name.lower():
                    await handler.handle(*args[1:])


cmd_terminal = Terminal()
