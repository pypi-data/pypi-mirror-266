from scrapy.commands.version import Command

from gzspidertools import __version__


class AyuCommand(Command):
    def short_desc(self):
        return "Print GzSpiderTools version"

    def run(self, args, opts):
        print(f"GzSpiderTools {__version__}")
