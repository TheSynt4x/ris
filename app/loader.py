import os

from app.core import logger, settings
from app.libs import db
from app.utils import find_in_sql_tuple


def load_subreddits_from_file():
    """
    Load subreddits from text file into Pydantic settings
    """
    subs = []

    with open("subreddits.txt") as f:
        subs.extend([s.strip() for s in f.readlines()])

    return subs


def load_categories_from_file():
    if not os.path.exists("categories"):
        logger.info("no categories")
        return

    cats = {}

    for file in os.listdir("categories"):
        if not file.endswith(".txt"):
            continue

        category = file.rsplit(".", 1)[0]

        with open(f"categories/{file}") as f:
            for c in f.readlines():
                if category not in cats:
                    cats[category] = [c.strip()]
                else:
                    cats[category].append(c.strip())

    return cats


async def load_subreddits_from_db():
    db_subreddits = await db._get("SELECT id, name FROM subreddits")

    return [s[1] for s in db_subreddits]


async def load_categories_from_db():
    db_categories = await db._get("SELECT id, name, subreddit FROM categories")

    cats = {}

    for (_, name, subreddit) in db_categories:
        if name not in cats:
            cats[name.lower()] = [subreddit.lower()]
        else:
            cats[name.lower()].append(subreddit.lower())

    return cats


async def load_settings():
    db_settings = None

    if os.environ.get("DB_HOSTNAME") and os.environ.get("DB_DATABASE"):
        try:
            db_settings = await db.get_settings()
        except Exception:
            db_settings = None

    if not db_settings:
        settings.db_conn = False

        settings.subreddits = load_subreddits_from_file()
        settings.categories = load_categories_from_file()
    else:
        settings.db_conn = True

        settings.subreddits = await load_subreddits_from_db()
        settings.categories = await load_categories_from_db()

        settings.subreddits.extend(load_subreddits_from_file())
        settings.categories.update(load_categories_from_file())

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

    logger.info(f"db: {settings.db_conn}")
    logger.info(f"loaded: {settings.subreddits}")
    logger.info(f"loaded: {settings.categories}")
