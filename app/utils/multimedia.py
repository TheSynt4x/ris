import os
from io import BytesIO

import httpx
from PIL import Image, UnidentifiedImageError

from app.core import logger


async def save_image_from_url(url, name, format="png", save_to_dir=None, category=None):
    """
    Save an image from URL

    Arguments:
        - url: image URL
        - name: output name
        - format: set image output format
        - save_to_dir: which directory to save it to
    """

    directory = None
    if category and not save_to_dir:
        directory = category
    elif category and save_to_dir:
        directory = f"{category}/{save_to_dir}"
    elif save_to_dir:
        directory = save_to_dir

    if not os.path.exists(directory):
        os.makedirs(f"assets/{directory}", exist_ok=True)

    filename = f"{name}.{format}"
    if directory is not None:
        filename = f"{directory}/{filename}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        try:
            if os.path.isfile(f"assets/{filename}"):
                logger.info(f"skipping: {filename}")
                return

            image = Image.open(BytesIO(response.content))
            image.save(f"assets/{filename}")

            # TODO: setting for writing out names
            logger.info(f"saved: {filename}")
        except UnidentifiedImageError:
            return


async def save_video_from_url(url, name, format="mp4", save_to_dir=None, category=None):
    """
    Save video from URL

    Arguments:
        - url: video URL
        - name: output name
        - format: set video output format
        - save_to_dir: which directory to save it to
    """

    directory = None
    if category and not save_to_dir:
        directory = category
    elif category and save_to_dir:
        directory = f"{category}/{save_to_dir}"
    elif save_to_dir:
        directory = save_to_dir

    if not os.path.exists(directory):
        os.makedirs(f"assets/{directory}", exist_ok=True)

    filename = f"{name}.{format}"
    if directory is not None:
        filename = f"{directory}/{filename}"

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

    # TODO: setting for writing out names
    logger.info(f"saved: {filename}")
