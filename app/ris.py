import asyncio
import os

from asyncpraw import Reddit

from app.core import logger, settings
from app.libs import db, praw
from app.utils import find_in_sql_tuple


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


async def load_subreddits_from_db():
    db_subreddits = await db._get("SELECT id, name FROM subreddits")
    settings.subreddits = [s[1] for s in db_subreddits]

    logger.info(f"loaded: {settings.subreddits}")


async def load_categories_from_db():
    db_categories = await db._get("SELECT id, name, subreddit FROM categories")

    for (_, name, subreddit) in db_categories:
        if name not in settings.categories:
            settings.categories[name.lower()] = [subreddit.lower()]
        else:
            settings.categories[name.lower()].append(subreddit.lower())

    logger.info(f"loaded: {settings.categories}")


async def load_settings():
    try:
        db_settings = await db.get_settings()
    except Exception:
        db_settings = None

    if not db_settings:
        load_subreddits_from_file()
        load_categories_from_file()
    else:
        await load_subreddits_from_db()
        await load_categories_from_db()

        if not (settings.client_id and settings.client_secret):
            logger.info("no client id set from sh file, loading from db")

            settings.client_id = find_in_sql_tuple(db_settings, "client_id")
            settings.client_secret = find_in_sql_tuple(db_settings, "client_secret")

            if not (settings.client_id and settings.client_secret):
                logger.error("could not establish connection")

        username = find_in_sql_tuple(db_settings, "username")
        password = find_in_sql_tuple(db_settings, "password")

        if username and password:
            logger.error("connection must be established from sh file for user creds")

        # todo: dropbox api token


async def main():
    """
    Main entry point
    """

    await load_settings()

    async with Reddit(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        user_agent=settings.user_agent,
        username=settings.username,
        password=settings.password,
    ) as reddit:
        subreddits = []

        if settings.categories.values():
            for category, subs in settings.categories.items():
                for subreddit in subs:
                    if subreddit in settings.subreddits:
                        continue

                    subreddits.append(praw.get_submissions(reddit, subreddit, category))

        for subreddit in settings.subreddits:
            subreddits.append(praw.get_submissions(reddit, subreddit))

        logger.info(f"fetching content from {len(subreddits)} subs")

        await asyncio.gather(*subreddits)
