from aioconsole import ainput

from app.core import logger, settings


class Config:
    name = "config"

    async def handle(self, *args):
        if args[0] == "webhook":
            # config webhook {url}

            settings.webhook_url = await ainput("webhook: ")

            logger.info(f"webhook: {settings.webhook_url}")

        elif args[0] == "subreddits" and len(args) == 2:
            # config subreddits {num}

            settings.subreddits.extend(
                [await ainput("subreddit: ") for _ in range(int(args[1]))]
            )

            logger.info(f"loaded: {settings.subreddits}")

        elif args[0] == "categories" and len(args) == 3:
            # config categories nsfw 2

            cats = {args[1]: [await ainput("subreddit: ") for _ in range(int(args[2]))]}
            settings.categories.update(cats)

            logger.info(f"loaded: {settings.categories}")
