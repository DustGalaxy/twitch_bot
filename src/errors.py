import yarl
from twitchio.ext import commands


class YoutubeConverterError(commands.BadArgument):
    def __init__(self, link: yarl.URL):
        self.link = link
        super().__init__("Bad link!")


class YTVideoTooLongError(commands.BadArgument):
    def __init__(self, time: int):
        self.time = time
        super().__init__("Video too long.")


class YTVideoFewViewsError(commands.BadArgument):
    def __init__(self, views: int):
        self.views = views
        super().__init__("Video has too few views.")