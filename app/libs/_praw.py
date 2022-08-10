import os
import sys

from asyncpraw import Reddit

from app.core import logger, settings
from app.libs import db
from app.utils.multimedia import save_image_from_url, save_video_from_url


class PRAW:
    async def get_submissions(self, reddit: Reddit, sub: str, cat: str = None) -> None:
        """
        Get reddit submissions and save them

        Arguments:
            - sub:  The subreddit from which you want to get submissions from
        """

        all_submissions_list = []

        submissions = await reddit.subreddit(sub)

        sub_id = None
        cat_id = None

        global_post_limit = settings.global_post_limit

        if settings.db_conn:
            db_subreddit = await db.get_subreddit_by_name(sub)

            if db_subreddit:
                sub_id = db_subreddit[0][0]
                global_post_limit = db_subreddit[0][2]

            if cat:
                db_category = await db.get_category_by_name(cat, sub)

                if db_category:
                    cat_id = db_category[0][0]
                    global_post_limit = db_category[0][3]

        try:
            async for submission in submissions.new(limit=global_post_limit):
                if settings.db_conn:
                    db_submission = await db.get_image_by_id(submission.id)

                    if db_submission is not None:
                        continue

                if submission.is_video:
                    url = submission.secure_media.get("reddit_video").get(
                        "fallback_url"
                    )

                    if not url:
                        continue

                    await save_video_from_url(
                        url,
                        name=submission.id,
                        save_to_dir=sub,
                        category=cat,
                    )

                    if settings.db_conn and (sub_id or cat_id):
                        all_submissions_list.append(
                            (submission.url, submission.id, "NEW", sub_id, cat_id)
                        )
                else:
                    await save_image_from_url(
                        url=submission.url,
                        name=submission.id,
                        save_to_dir=sub,
                        category=cat,
                    )

                    if settings.db_conn and (sub_id or cat_id):
                        all_submissions_list.append(
                            (submission.url, submission.id, "NEW", sub_id, cat_id)
                        )

                    if hasattr(submission, "gallery_data"):
                        ids = [
                            i["media_id"]
                            for i in submission.gallery_data.get("items", [])
                        ]

                        for id in ids:
                            if settings.db_conn:
                                if await db.get_image_by_id(id):
                                    continue

                            url = submission.media_metadata[id]["p"][0]["u"]
                            url = url.split("?")[0].replace("preview", "i")

                            await save_image_from_url(
                                url=url,
                                name=id,
                                save_to_dir=sub,
                                category=cat,
                            )

                            if settings.db_conn and (sub_id or cat_id):
                                all_submissions_list.append(
                                    (url, id, "NEW", sub_id, cat_id)
                                )

                    if hasattr(submission, "crosspost_parent_list"):
                        for crosspost in submission.crosspost_parent_list:
                            ids = [
                                i["media_id"]
                                for i in crosspost.get("gallery_data", {}).get(
                                    "items", []
                                )
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
                                    save_to_dir=sub,
                                    category=cat,
                                )

                                if settings.db_conn and (sub_id or cat_id):
                                    all_submissions_list.append(
                                        (url, id, "NEW", sub_id, cat_id)
                                    )

                if settings.db_conn and (sub_id or cat_id):
                    await db.create_submissions(all_submissions_list)
        except KeyboardInterrupt:
            await db.create_submissions(all_submissions_list)

            logger.info(f"submissions saved: {len(all_submissions_list)}")

            logger.info("graceful shutdown")

            try:
                sys.exit(0)
            except Exception:
                os._exit(0)


praw = PRAW()
