import aiohttp
import requests
import yarl
import json
import re
import isodate
from icecream import ic
from jose import jwt

from youtube_provaider import youtube
from loguru import logger
from src.errors import YTVideoTooLongError, YTVideoFewViewsError, YoutubeConverterError
from src.config import API_KEY, API_URL, ALGORITHM, CONFIG_EX_SECONDS
from src.redis_init import redis_client


async def add_music(details: dict, from_user: str, to_user: str, config: dict, priority: int) -> str:
    url = API_URL + '/order/new_order'
    payload = {
                "video_id": details['video_id'],
                'title': details['title'],
                'length': details['length'],
                "sendler": from_user,
                "username": to_user,
                "is_active": True,
                "in_statistics": config["in_statistics"],
                "priority": priority
    }
    encoded_jwt = jwt.encode(payload, API_KEY, algorithm=ALGORITHM)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={"token": encoded_jwt}
        ) as response:
            if response.status == 201:
                logger.info("Order has been successfully created")
                return "OK"
            else:
                logger.info("Order creating failed")
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


def youtube_parser(url: str) -> str | None:
    """
    Извлекает идентификатор видео YouTube из URL.

    Аргументы:
    url (str): URL-адрес видео YouTube

    Возвращает:
    str: Идентификатор видео YouTube (11 символов) или None, если URL некорректный

    Поддерживает:
    http://www.youtube.com/watch?v=id123456789&feature=feedrec_grec_index
    http://www.youtube.com/user/IngridMichaelsonVEVO#p/a/u/1/id123456789
    http://www.youtube.com/v/id123456789?fs=1&amp;hl=en_US&amp;rel=0
    http://www.youtube.com/watch?v=id123456789#t=0m10s
    http://www.youtube.com/embed/id123456789?rel=0
    http://www.youtube.com/watch?v=id123456789
    http://youtu.be/id123456789
    """
    regex = re.compile(r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*', )
    match = re.match(regex, url)
    return match.group(7) if match and len(match.group(7)) == 11 else None


def get_yt_video_details(url: str):

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=youtube_parser(url),
    )
    response = request.execute()

    if not len(response['items']):
        raise ValueError()

    return {
        'title': response['items'][0]['snippet']['title'],
        'video_id': response['items'][0]["id"],
        'length': isodate.parse_duration(response['items'][0]['contentDetails']['duration']).seconds,
        'views': response['items'][0]['statistics']['viewCount'],
    }

    # yt = YouTube(url)
    # return {
    #     'title': yt.title,
    #     'video_id': yt.video_id,
    #     'length': yt.length,
    #     'views': yt.views,
    #     'thumbnail_url': yt.thumbnail_url,
    # }


async def video_verifier(details: dict, config: dict):
    if int(details["length"]) > config["len"]:
        raise YTVideoTooLongError(details["length"])
    elif int(details["views"]) < config["views"]:
        raise YTVideoFewViewsError(details["views"])
