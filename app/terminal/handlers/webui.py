from app.core import logger


class WebUI:
    name = "webui"

    async def handle(self, *args):
        logger.info("run make webui in another terminal window")
