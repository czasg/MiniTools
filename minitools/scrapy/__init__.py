import scrapy
import subprocess

from .__pager import *
from .__utils import *
from .__xpather import *

__all__ = (__pager.__all__ +
           __utils.__all__ +
           __xpather.__all__)


class miniSpider(scrapy.Spider):
    name = "minitools"

    mini_proxy = None

    @classmethod
    def run(cls,
            spiderName=None,
            suffix="",
            single=True,
            save=False,
            check_logger_files=False):
        """
        >>> from minitools.scrapy import miniSpider
        >>> class MySpider(miniSpider):
        >>>     name = "spider name isn't strong correlation"
        >>>     ...
        >>> MySpider.run(__file__)
        Use MySpider.run(__file__), so you can load spider faster.
        :param spiderName: general means `__file__`
        :param suffix: you can add some config if need
        :param single: run just one spider rather scanning all spider in project
        :param save: save item as json by `FEED_URI`
        :param check_logger_files:
        :return:
        """
        command = "crawl"

        if single:
            assert spiderName, "You may should run(single=False)"
            command = "runspider"
            # By command of `runspider`, this `SPIDER_LOADER_CLASS` may not make any sense.
            suffix += " -s SPIDER_LOADER_CLASS=minitools.scrapy.spiderloader.SingleSpiderLoader "
        else:
            spiderName = cls.name

        if save:
            if save is True:  # default, we use json to save
                suffix += f" -o {cls.name}.json -s FEED_EXPORT_ENCODING=utf-8 "
            else:
                suffix += f" -o {save} -s FEED_EXPORT_ENCODING=utf-8 "

        if check_logger_files:
            from time import time
            from minitools import to_path
            # LOG_FILE_PATH = cls.check_logger_files()
            # logFileName = f"{cls.name}_{int(time())}.log"
            # suffix += f" -s LOG_FILE={to_path(LOG_FILE_PATH, logFileName)} "  # todo, this is stupid

        subprocess.call(f'scrapy {command} {spiderName} {suffix}', shell=True)
