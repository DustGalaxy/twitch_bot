import aiohttp
import requests
import yarl
import json
from jose import jwt

from pytube import YouTube
from loguru import logger
from src.errors import YTVideoTooLongError, YTVideoFewViewsError, YoutubeConverterError
from src.config import API_KEY, API_URL, ALGORITHM, CONFIG_EX_SECONDS
from src.redis_init import redis_client


async def add_music(details: dict, from_user: str, to_user: str) -> str:
    url = API_URL + '/order/new_order'
    payload = {
                "video_id": details['video_id'],
                'title': details['title'],
                "thumbnail_url": details['thumbnail_url'],
                'length': details['length'],
                "sendler": from_user,
                "username": to_user
    }
    encoded_jwt = jwt.encode(payload, API_KEY, algorithm=ALGORITHM)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"token": encoded_jwt}
        ) as response:

            logger.info(await response.json())
            if response.status == 200:
                return "OK"
            else:
                return "FAIL"


def get_user_config(username: str) -> dict[str, str]:
    r"""
    Return bot config for username
    """

    json_conf = redis_client.get(username)
    if json_conf:
        config = json.loads(json_conf)
        logger.info(f"Was get {username} config from Redis")
        return config

    url = API_URL + '/users/get_config'
    data = {"sub": username}
    encoded_jwt = jwt.encode(data, API_KEY, algorithm=ALGORITHM)
    token = {"token": encoded_jwt}

    response = requests.get(url, params=token)

    config = response.json()
    save_config = json.dumps(config)
    redis_client.set(name=username, value=save_config, ex=int(CONFIG_EX_SECONDS))

    logger.info(f"Was get {username} config from API")
    return config


def youtube_converter(arg: str) -> str:
    url = yarl.URL(arg)
    if url.host not in ("www.youtube.com", "youtube.com", "youtu.be"):
        raise YoutubeConverterError(url)

    return url.__str__()


def get_yt_video_details(url: str):
    yt = YouTube(url)

    return {
        'title': yt.title,
        'video_id': yt.video_id,
        'length': yt.length,
        'views': yt.views,
        'thumbnail_url': yt.thumbnail_url,
    }


async def video_verifier(details: dict, username: str):

    config = get_user_config(username)
    if details["length"] > config["len"]:
        raise YTVideoTooLongError(details["length"])
    elif details["views"] < config["views"]:
        raise YTVideoFewViewsError(details["views"])
