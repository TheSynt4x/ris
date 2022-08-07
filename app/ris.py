import asyncio
import os

from asyncpraw import Reddit

from app.core import logger, settings
from app.libs import praw


def load_subreddits_from_file():
    """
    Load subreddits from text file into Pydantic settings
    """

    with open("subreddits.txt") as f:
        settings.subreddits = [s.strip() for s in f.readlines()]

    logger.info(f"loaded: {settings.subreddits}")


def load_categories_from_file():
    if not os.path.exists("categories"):
        logger.info("no categories")
        return

    for file in os.listdir("categories"):
        if not file.endswith(".txt"):
            continue

        category = file.rsplit(".", 1)[0]

        with open(f"categories/{file}") as f:
            for c in f.readlines():
                if category not in settings.categories:
                    settings.categories[category] = [c.strip()]
                else:
                    settings.categories[category].append(c.strip())

    logger.info(f"loaded: {settings.categories}")


async def main():
    """
    Main entry point
    """

    load_subreddits_from_file()
    load_categories_from_file()

    async with Reddit(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        user_agent=settings.user_agent,
        username=settings.username,
        password=settings.password,
    ) as reddit:
        subreddits = []

        if os.path.exists("categories"):
            for category, subs in settings.categories.items():
                for subreddit in subs:
                    if subreddit in settings.subreddits:
                        continue

                    subreddits.append(praw.get_submissions(reddit, subreddit, category))

        for subreddit in settings.subreddits:
            subreddits.append(praw.get_submissions(reddit, subreddit))

        logger.info(f"fetching content from {len(subreddits)} subs")

        await asyncio.gather(*subreddits)
