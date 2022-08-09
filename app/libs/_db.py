import tormysql

from app.utils import types


class DatabaseWrapper:
    def __init__(self) -> None:
        self.pool = tormysql.helpers.ConnectionPool(
            max_connections=20,
            idle_seconds=7200,
            wait_connection_timeout=3,
            host="127.0.0.1",
            user="user1",
            passwd="1234",
            db="ris",
            charset="utf8",
        )

    async def _get(self, sql, *args):
        """
        Executes any SQL query with arguments and retrieves results from it

        Arguments:
            - sql: sql query
            - args: arguments to pass into the query
        """

        cursor = await self.pool.execute(sql, *args)

        return cursor.fetchall()

    async def get(self, table, limit=None):
        """
        Generic method for getting results from a table

        Arguments:
            - table: which table to get results from
            - limit: number of posts to get
        """

        sql = f"SELECT id, url FROM {table}"

        if limit is not None:
            sql += f" LIMIT {limit}"

        return await self._get(sql)

    async def get_images_by_category(self, category_id, type=types.NEW):
        """
        Get images by category id and type

        Arguments:
            - category: which category to get from
            - type: which type to get
        """

        sql = """
            SELECT reddit_image_id, url, category_id, timestamp
            FROM images WHERE category_id = %s AND type = %s
        """

        return await self._get(sql, (category_id, type))

    async def get_images_by_subreddit(self, subreddit_id, type=types.NEW):
        """
        Get images by subreddit id and type

        Arguments:
            - category: which category to get from
            - type: which type to get
        """

        sql = """
            SELECT reddit_image_id, url, subreddit_id, timestamp
            FROM images WHERE subreddit_id = %s AND type = %s
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
            FROM images WHERE reddit_image_id = %s
        """

        return await self._get(sql, reddit_image_id)

    async def create_image(
        self, url, reddit_image_id, subreddit_id=None, category_id=None
    ):
        """
        Create a new image entity

        Arguments:
            - url: image url
            - reddit_image_id: reddit's internal ID for the image
            - subreddit_id: which subreddit it was posted to
            - category_id: which category it should be saved under
        """

        sql = """
            INSERT INTO images
                (url, reddit_image_id, subreddit_id, category_id, NOW())
            VALUES
                (%s, %s, %s, %s)
        """

        async with await self.pool.begin() as tx:
            await tx.execute(sql, (url, reddit_image_id, subreddit_id, category_id))

    async def get_settings(self):
        """
        Get RIS settings
        """

        return await self._get("SELECT k, v FROM settings")


db = DatabaseWrapper()
