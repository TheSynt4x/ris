import asyncio

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


async def main():
    """
    Main entry point
    """

    load_subreddits_from_file()

    async with Reddit(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        user_agent=settings.user_agent,
        username=settings.username,
        password=settings.password,
    ) as reddit:
        subreddits = [
            praw.get_submissions(reddit, subreddit) for subreddit in settings.subreddits
        ]

        await asyncio.gather(*subreddits)
