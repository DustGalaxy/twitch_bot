import twitchio
from loguru import logger

from twitchio.ext import commands

from bot_module import bot
from src.errors import YTVideoTooLongError, YTVideoFewViewsError, YoutubeConverterError
from utils import video_verifier, youtube_converter, add_music, get_yt_video_details, get_user_config


@bot.command(name="test")
async def test(ctx: commands.Context):
    msg = f"@{ctx.author.name} test passed!"
    await ctx.send(msg)
    logger.info(f"Executed command: test, message send: {msg}")


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    msg = f"pong"
    await ctx.send(msg)
    logger.info(f"Executed command: ping, message send: {msg}")


@bot.command(name="help")
async def help_command(ctx: commands.Context,  user: twitchio.User):
    msg = f"@{ctx.author.name} У меня есть следующие команды: test, help, mr."
    await ctx.send(msg)

    logger.info(f"Executed command: help, message send: {msg}")


cmd: bool = False


@bot.command(name="mr")
async def mr_command(ctx: commands.Context, arg: str | None):
    if arg is None:
        await ctx.send("Это команда для заказа музыки, её включают модеры или стример. Пример команды: !mr https://youtu.be/dQw4w9WgXcQ")
        return

    global cmd

    if arg in ["on", "off"] and (ctx.author.is_mod or ctx.author.is_broadcaster):
        match arg:
            case "on":
                if not cmd:
                    cmd = True
                    await ctx.send("Заказ музыки включён.")
                    logger.info(f"{ctx.author.name} включил заказ музыки.")

            case "off":
                if cmd:
                    cmd = False
                    await ctx.send("Заказ музыки выключен.")
                    logger.info(f"{ctx.author.name} выключил заказ музыки.")

        return

    if not cmd:
        await ctx.send("Заказ музыки сейчас не доступен.")
        logger.info(f"{ctx.author.name} попытался поставить музыку. url: {arg}")
        return

    config = get_user_config(ctx.channel.name)

    try:
        url = youtube_converter(arg)
        details = get_yt_video_details(url)
        await video_verifier(details, config)

    except YoutubeConverterError:
        await ctx.send(f"@{ctx.author.name} ссылка не поддерживается, поробуйте другую.")
        return

    except YTVideoTooLongError:
        await ctx.send("Видео слишком блинное.")
        return

    except YTVideoFewViewsError:
        await ctx.send("У видео маловато просмотров.")
        return

    priority_song = 1
    if ctx.author.is_broadcaster:
        priority_song = 99

    if await add_music(
            details,
            from_user=ctx.author.name,
            to_user=ctx.channel.name,
            config=config,
            priority=priority_song
    ) == "OK":
        msg: str = "Да, я поставлю этот трек для тебя! (нет)"
        await ctx.send(msg)
        logger.info(f"""
                        Executed command: mr, message send: {msg} 
                        | video id: {url} 
                        | channel name: {ctx.channel.name} 
                        | author name: {ctx.author.name}
                    """)
    else:
        msg: str = "Что то пошло не так! Обратитесь к разработчику!"
        await ctx.send(msg)
        logger.info(f"""
                        Executed command: mr, message send: {msg} 
                        | video id: {url} 
                        | channel name: {ctx.channel.name} 
                        | author name: {ctx.author.name}
                    """)


@bot.event()
async def event_ready():
    logger.info(f'Logged into Twitch | {bot.nick}')
    # r = await get_user_config(INIT_CHANNELS.split(" ")[0])
    # print(r)


@logger.catch
def main():
    logger.add(sink="../logs.log",
               format="{time} | {level} | {message}",
               level="INFO",
               rotation="06:00",
               compression="zip")

    bot.run()


if __name__ == '__main__':
    main()
