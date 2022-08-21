import os
import sys

from asyncpraw import Reddit

from app.core import logger, settings
from app.libs import db
from app.utils import types
from app.utils.multimedia import save_image_from_url, save_video_from_url


class PRAW:
    def __init__(self, sub, cat=None):
        self.sub = sub
        self.cat = cat

        self.sub_id = None
        self.cat_id = None
        self.global_post_limit = None

    @property
    def has_db_connection(self):
        return settings.db_conn and (self.sub_id or self.cat_id)

    async def _get_db_info(self):
        """
        Get subreddit id, category id and global post limit
        for each subreddit and category

        Arguments:
            - sub: subreddit
            - cat: category
        """

        self.global_post_limit = settings.global_post_limit

        if settings.db_conn:
            db_subreddit = await db.get_subreddit_by_name(self.sub)

            if db_subreddit:
                self.sub_id = db_subreddit[0][0]
                self.global_post_limit = db_subreddit[0][2]

            if self.cat:
                db_category = await db.get_category_by_name(self.cat, self.sub)

                if db_category:
                    self.cat_id = db_category[0][0]
                    self.global_post_limit = db_category[0][3]

    async def _save_video(self, submission):
        """
        Save video for submission
        """

        url = submission.secure_media.get("reddit_video").get("fallback_url")

        if not url:
            return None

        await save_video_from_url(
            url,
            name=submission.id,
            save_to_dir=self.sub,
            category=self.cat,
        )

        if self.has_db_connection:
            return (submission.url, submission.id, "NEW", self.sub_id, self.cat_id)

        return None

    async def _save_gallery_data(self, submission):
        """
        Save submission gallery data
        """
        gallery_data = []

        for id in [i["media_id"] for i in submission.gallery_data.get("items", [])]:
            if settings.db_conn:
                if await db.get_image_by_id(id):
                    continue

            url = submission.media_metadata[id]["p"][0]["u"]
            url = url.split("?")[0].replace("preview", "i")

            await save_image_from_url(
                url=url,
                name=id,
                save_to_dir=self.sub,
                category=self.cat,
            )

            if self.has_db_connection:
                gallery_data.append((url, id, "NEW", self.sub_id, self.cat_id))

        return gallery_data

    async def _save_crosspost_parent_list(self, submission):
        """
        Save crosspost gallery data
        """

        crosspost_gallery_data = []

        for crosspost in submission.crosspost_parent_list:
            ids = [
                i["media_id"]
                for i in crosspost.get("gallery_data", {}).get("items", [])
            ]

            for id in ids:
                if settings.db_conn:
                    if await db.get_image_by_id(id):
                        continue

                url = crosspost["media_metadata"][id]["p"][0]["u"]
                url = url.split("?")[0].replace("preview", "i")

                await save_image_from_url(
                    url=url,
                    name=id,
                    save_to_dir=self.sub,
                    category=self.cat,
                )

                if self.has_db_connection:
                    crosspost_gallery_data.append(
                        (url, id, "NEW", self.sub_id, self.cat_id)
                    )

        return crosspost_gallery_data

    async def _save_submission_data(self, submission):
        await save_image_from_url(
            url=submission.url,
            name=submission.id,
            save_to_dir=self.sub,
            category=self.cat,
        )

        if self.has_db_connection:
            return (
                submission.url,
                submission.id,
                "NEW",
                self.sub_id,
                self.cat_id,
            )

        return None

    async def get_submissions(
        self, reddit: Reddit, section: str = types.NEW, limit=None
    ) -> None:
        """
        Get reddit submissions and save them

        Arguments:
            - sub:  The subreddit from which you want to get submissions from
        """

        all_submissions_list = []

        submissions = await reddit.subreddit(self.sub)

        await self._get_db_info()

        post_limit = limit if limit is not None else self.global_post_limit

        if section == types.NEW:
            submissions = submissions.new(limit=post_limit)
        elif section == types.HOT:
            submissions = submissions.hot(limit=post_limit)
        elif section == types.TOP:
            submissions = submissions.top(limit=post_limit)

        try:
            async for submission in submissions:
                if not (
                    submission.url.startswith("http://")
                    or submission.url.startswith("https://")  # noqa
                ):
                    continue

                if settings.db_conn:
                    db_submission = await db.get_image_by_id(submission.id)

                    if db_submission is not None:
                        continue

                if submission.is_video:
                    video = await self._save_video(submission)

                    if video is not None:
                        all_submissions_list.append(video)
                else:
                    submission_image = await self._save_submission_data(submission)

                    if submission_image:
                        all_submissions_list.append(submission_image)

                    if hasattr(submission, "gallery_data"):
                        all_submissions_list.extend(
                            await self._save_gallery_data(submission)
                        )

                    if hasattr(submission, "crosspost_parent_list"):
                        all_submissions_list.extend(
                            await self._save_crosspost_parent_list(
                                submission,
                            )
                        )

                if self.has_db_connection:
                    await db.create_submissions(all_submissions_list)
                    logger.info(f"submissions saved: {len(all_submissions_list)}")

        except KeyboardInterrupt:
            await db.create_submissions(all_submissions_list)

            logger.info(f"submissions saved: {len(all_submissions_list)}")

            logger.info("graceful shutdown")

            try:
                sys.exit(0)
            except Exception:
                os._exit(0)


praw = PRAW
