import os
from io import BytesIO

import httpx
from PIL import Image, UnidentifiedImageError

from app.core import logger


async def save_image_from_url(url, name, format="png", save_to_dir=None):
    """
    Save an image from URL

    Arguments:
        - url: image URL
        - name: output name
        - format: set image output format
        - save_to_dir: which directory to save it to
    """
    filename = f"{name}.{format}"

    if save_to_dir:
        if not os.path.exists(save_to_dir):
            os.makedirs(f"assets/{save_to_dir}", exist_ok=True)

        filename = f"{save_to_dir}/{name}.{format}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        try:
            if os.path.isfile(f"assets/{filename}"):
                logger.info(f"skipping: {filename}")
                return

            image = Image.open(BytesIO(response.content))
            image.save(f"assets/{filename}")

            logger.info(f"saved: {filename}")
        except UnidentifiedImageError:
            return


async def save_video_from_url(url, name, format="mp4", save_to_dir=None):
    """
    Save video from URL

    Arguments:
        - url: video URL
        - name: output name
        - format: set video output format
        - save_to_dir: which directory to save it to
    """

    filename = f"{name}.{format}"

    if save_to_dir:
        if not os.path.exists(save_to_dir):
            os.makedirs(f"assets/{save_to_dir}", exist_ok=True)

        filename = f"{save_to_dir}/{name}.{format}"

    if os.path.isfile(f"assets/{filename}"):
        logger.info(f"skipping: {filename}")
        return

    with open(f"assets/{filename}", "wb") as video:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as response:
                async for data in response.aiter_bytes():
                    if not data:
                        break

                    video.write(data)

    logger.info(f"saved: {filename}")
