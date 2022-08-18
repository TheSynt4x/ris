import tormysql

from app.core import settings
from app.utils import types


class DatabaseWrapper:
    def __init__(self) -> None:
        self.create_pool(
            settings.db_hostname,
            settings.db_username,
            settings.db_password,
            settings.db_database,
        )

    def create_pool(self, hostname, username, password, database):
        self.pool = tormysql.helpers.ConnectionPool(
            max_connections=20,
            idle_seconds=7200,
            wait_connection_timeout=3,
            host=hostname,
            user=username,
            passwd=password,
            db=database,
            charset="utf8",
        )

    async def _get(self, sql, *args, cursor_cls=None):
        """
        Executes any SQL query with arguments and retrieves results from it

        Arguments:
            - sql: sql query
            - args: arguments to pass into the query
        """

        cursor = await self.pool.execute(sql, *args, cursor_cls=cursor_cls)

        return cursor.fetchall()

    async def get(self, table, limit=None, cursor_cls=None):
        """
        Generic method for getting results from a table

        Arguments:
            - table: which table to get results from
            - limit: number of posts to get
        """

        sql = f"SELECT id, url FROM {table}"

        if limit is not None:
            sql += f" LIMIT {limit}"

        return await self._get(sql, cursor_cls=cursor_cls)

    async def get_submissions_by_category(self, category_id, type=types.NEW):
        """
        Get submissions by category id and type

        Arguments:
            - category: which category to get from
            - type: which type to get
        """

        sql = """
            SELECT reddit_image_id, url, category_id, timestamp
            FROM submissions WHERE category_id = %s AND type = %s
        """

        return await self._get(sql, (category_id, type))

    async def get_submissions_by_subreddit(self, subreddit_id, type=types.NEW):
        """
        Get submissions by subreddit id and type

        Arguments:
            - category: which category to get from
            - type: which type to get
        """

        sql = """
            SELECT reddit_image_id, url, subreddit_id, timestamp
            FROM submissions WHERE subreddit_id = %s AND type = %s
        """

        return await self._get(sql, (subreddit_id, type))

    async def get_image_by_id(self, reddit_image_id):
        """
        Get image by reddit's image id

        Arguments:
            reddit_image_id: reddit's internal ID for the image
        """

        sql = """
            SELECT reddit_image_id, url, subreddit_id, category_id, timestamp
            FROM submissions WHERE reddit_image_id = %s
        """

        image = await self._get(sql, reddit_image_id)

        if not len(image):
            return None

        return image

    async def create_submissions(self, data):
        """
        Create submissions with batching call

        Arguments:
            - data: list of tuples containing id, sub_id and cat_id
        """

        sql = """
            INSERT INTO submissions
                (url, reddit_image_id, type, subreddit_id, category_id)
            VALUES (%s, %s, %s, %s, %s);
        """

        async with await self.pool.begin() as transaction:
            await transaction.executemany(sql, data)

    async def get_settings(self):
        """
        Get RIS settings
        """

        return await self._get("SELECT k, v FROM settings")

    async def get_subreddit_by_name(self, name):
        return await self._get(
            "SELECT id, name, post_limit FROM subreddits WHERE name = %s", (name)
        )

    async def get_category_by_name(self, name, sub):
        sql = """
            SELECT id, name, subreddit, post_limit FROM categories
            WHERE name = %s AND subreddit = %s
        """

        return await self._get(sql, (name, sub))


db = DatabaseWrapper()
