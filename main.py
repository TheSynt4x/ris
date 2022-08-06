import asyncio
import os
import sys

from app import ris
from app.core import logger

if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(ris.main())
    except Exception as e:
        logger.info(e)
    except KeyboardInterrupt:
        logger.info("exiting")

        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
