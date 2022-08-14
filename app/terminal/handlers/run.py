import asyncio

import httpx
from asyncpraw import Reddit

from app import libs
from app.core import logger, settings


class Run:
    name = "run"

    async def handle(self, *args):
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

                        subreddits.append(
                            libs.praw.get_submissions(reddit, subreddit, category)
                        )

            for subreddit in settings.subreddits:
                subreddits.append(libs.praw.get_submissions(reddit, subreddit))

            logger.info(f"fetching content from {len(subreddits)} subs")

            await asyncio.gather(*subreddits)

            uploaded_url = None
            if settings.mega_username and settings.mega_password:
                uploaded_url = libs.upload.upload()

            if uploaded_url and settings.webhook_url:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        settings.webhook_url, json={"content": uploaded_url}
                    )
