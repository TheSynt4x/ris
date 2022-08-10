import asyncio

import pymysql.err

from app import ris
from app.core import logger

if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(ris.main())
    except KeyboardInterrupt:
        logger.info("exiting")
    except pymysql.err.OperationalError:
        logger.info("exiting")
