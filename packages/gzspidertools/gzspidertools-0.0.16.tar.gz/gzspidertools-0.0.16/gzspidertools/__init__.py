from gzspidertools.items import AyuItem
from gzspidertools.scraper.http.request import AiohttpRequest
from gzspidertools.scraper.http.request.form import AiohttpFormRequest
from gzspidertools.scraper.spiders import AyuSpider
from gzspidertools.scraper.spiders.crawl import AyuCrawlSpider

__all__ = [
    "AiohttpRequest",
    "AiohttpFormRequest",
    "AyuItem",
    "AyuSpider",
    "AyuCrawlSpider",
    "__version__",
]

__version__ = "0.0.16"
