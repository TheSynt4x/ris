from asyncpraw import Reddit

from app.core import settings
from app.libs import db
from app.utils import find_in_sql_tuple
from app.utils.multimedia import save_image_from_url, save_video_from_url


class PRAW:
    async def get_submissions(self, reddit: Reddit, sub: str, cat: str = None) -> None:
        """
        Get reddit submissions and save them

        Arguments:
            - sub:  The subreddit from which you want to get submissions from
        """

        subreddit = await reddit.subreddit(sub)

        sub_id = None
        cat_id = None
        if settings.db_conn:
            sub_id = find_in_sql_tuple(await db.get_subreddit_by_name(sub), "id")

            if cat:
                cat_id = find_in_sql_tuple(await db.get_category_by_name(cat), "id")

        async for submission in subreddit.new(limit=1):
            db_submission = await db.get_image_by_id(submission.id)

            if db_submission:
                continue

            if submission.is_video:
                url = submission.secure_media.get("reddit_video").get("fallback_url")

                if not url:
                    continue

                await save_video_from_url(
                    url,
                    name=submission.id,
                    save_to_dir=sub,
                    category=cat,
                )

                if settings.db_conn and (sub_id or cat_id):
                    await db.create_image(submission.url, submission.id, sub_id, cat_id)
            else:
                await save_image_from_url(
                    url=submission.url,
                    name=submission.id,
                    save_to_dir=sub,
                    category=cat,
                )

                if settings.db_conn and (sub_id or cat_id):
                    await db.create_image(submission.url, submission.id, sub_id, cat_id)

                if hasattr(submission, "gallery_data"):
                    ids = [
                        i["media_id"] for i in submission.gallery_data.get("items", [])
                    ]

                    for id in ids:
                        url = submission.media_metadata[id]["p"][0]["u"]
                        url = url.split("?")[0].replace("preview", "i")

                        await save_image_from_url(
                            url=url,
                            name=id,
                            save_to_dir=sub,
                            category=cat,
                        )

                        if settings.db_conn and (sub_id or cat_id):
                            await db.create_image(
                                submission.url, submission.id, sub_id, cat_id
                            )

                if hasattr(submission, "crosspost_parent_list"):
                    for crosspost in submission.crosspost_parent_list:
                        ids = [
                            i["media_id"]
                            for i in crosspost.get("gallery_data", {}).get("items", [])
                        ]

                        for id in ids:
                            url = crosspost["media_metadata"][id]["p"][0]["u"]
                            url = url.split("?")[0].replace("preview", "i")

                            await save_image_from_url(
                                url=url,
                                name=id,
                                save_to_dir=sub,
                                category=cat,
                            )

                            if settings.db_conn and (sub_id or cat_id):
                                await db.create_image(
                                    submission.url, submission.id, sub_id, cat_id
                                )


praw = PRAW()
