from asyncpraw import Reddit

from app.utils.multimedia import save_image_from_url, save_video_from_url


class PRAW:
    async def get_submissions(self, reddit: Reddit, sub: str) -> None:
        """
        Get reddit submissions and save them

        Arguments:
            - sub:  The subreddit from which you want to get submissions from
        """

        subreddit = await reddit.subreddit(sub)

        async for submission in subreddit.new(limit=100):
            print(submission.url)

            if submission.is_video:
                url = submission.secure_media.get("reddit_video").get("fallback_url")

                if not url:
                    return

                await save_video_from_url(
                    url,
                    name=submission.id,
                    save_to_dir=sub,
                )
            else:
                await save_image_from_url(
                    url=submission.url,
                    name=submission.id,
                    save_to_dir=sub,
                )

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
                            )


praw = PRAW()
