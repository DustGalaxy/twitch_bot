from dotenv import load_dotenv
import os

load_dotenv()

TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.environ.get("TWITCH_SECRET")

O_AUTH_TOKEN = os.environ.get("O_AUTH_TOKEN")

API_KEY = os.environ.get("API_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
API_URL = os.environ.get("API_URL")

BOT_NICK = os.environ.get("BOT_NICK")

INIT_CHANNELS = os.environ.get("INIT_CHANNELS")

YOUTUBE_KEY = os.environ.get("YOUTUBE_KEY")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

CONFIG_EX_SECONDS = os.environ.get("CONFIG_EX_SECONDS")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")