import scrapy
import subprocess

from .__pager import *
from .__xpather import *

__all__ = (__pager.__all__ +
           __xpather.__all__)


class miniSpider(scrapy.Spider):
    name = "minitools"

    @classmethod
    def run(cls, spiderName=None, suffix="", single=True):
        """
        >>> from minitools.scrapy import miniSpider
        >>> class MySpider(miniSpider):
        >>>     name = "fastSpider_or_other"
        >>>     ...
        >>> MySpider.run(__file__)
        Use MySpider.run(__file__), so you can load spider faster.
        :param spiderName: general means `__file__`
        :param suffix: you can add some config if need
        :return:
        """
        if single:
            suffix += " -s SPIDER_LOADER_CLASS=minitools.scrapy.spiderloader.SingleSpiderLoader"
        subprocess.call(f'scrapy crawl {spiderName or cls.name} {suffix}', shell=True)
