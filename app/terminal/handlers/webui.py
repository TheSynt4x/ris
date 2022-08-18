from app.core import logger


class WebUI:
    name = "webui"

    async def handle(self, *args):
        # todo: look more into subprocess and other solutions

        logger.info("run make webui in another terminal window")
