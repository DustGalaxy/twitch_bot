import twitchio
from loguru import logger
from twitchio.ext import commands

from config import BOT_NICK, O_AUTH_TOKEN, TWITCH_CLIENT_ID, INIT_CHANNELS
from src.errors import YoutubeConverterError
from src.utils import get_user_config


class MyBot(commands.Bot):
    async def event_command_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.ArgumentParsingFailed):
            msg = error.message
            await context.send(msg)
            logger.error(msg)

        elif isinstance(error, commands.MissingRequiredArgument):
            msg = "You're missing an argument: " + error.name
            await context.send(msg)
            logger.error(msg)

        elif isinstance(error, commands.CheckFailure):
            msg = "Sorry, you cant run that command: " + error.args[0]
            await context.send(msg)
            logger.error(msg)

        elif isinstance(error, YoutubeConverterError):
            msg = f"{error.link} is not a valid youtube URL!"
            await context.send(msg)
            logger.error(msg)

        else:
            logger.error(error)


async def prefix_callback(bot: commands.Bot, message: twitchio.Message) -> str:
    r"""
    Return bot prefix for current chanel
    """

    config = get_user_config(message.channel.name)
    return config["prefix"]

    # async with async_session_maker() as session:
    #     stmt = select(User).where(User.username.ilike(message.channel.name))
    #     res = await session.execute(stmt)
    #     return res.scalar_one_or_none().config["prefix"]


def get_initial_channels():
    logger.info("Get initial channels")
    return INIT_CHANNELS.split(" ")


bot = MyBot(
    token=O_AUTH_TOKEN,
    client_id=TWITCH_CLIENT_ID,
    nick=BOT_NICK,
    prefix=prefix_callback,
    initial_channels=get_initial_channels()
)

