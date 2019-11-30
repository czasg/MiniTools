# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import re

from zope.interface import implementer
from importlib import import_module
from scrapy.utils.misc import walk_modules
from scrapy.interfaces import ISpiderLoader
from scrapy.utils.conf import closest_scrapy_cfg
from scrapy.utils.spider import iter_spider_classes

SEP2POINT = re.compile(r'[/\\]+').sub
SINGLE_SPIDER_LOADER = {
    'SPIDER_LOADER_CLASS': {
        'minitools.scrapy.spiderloader.SingleSpiderLoader': 0
    }
}


@implementer(ISpiderLoader)
class SingleSpiderLoader(object):

    def __init__(self, settings):
        self.settings = settings
        self.scrapy_module_path = os.path.dirname(closest_scrapy_cfg())
        self.spider_modules = settings.getlist('SPIDER_MODULES')

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def load(self, spider_name):
        if os.path.exists(spider_name):
            spider_path = self._get_spider_path(spider_name)
            spider_module = import_module(spider_path)
            for spider_cls in iter_spider_classes(spider_module):
                return spider_cls  # return the first spider module
        else:
            for name in self.spider_modules:
                for module in walk_modules(name):
                    for spider_cls in iter_spider_classes(module):
                        # print(spider_cls)
                        if spider_cls.name == spider_name:
                            return spider_cls
            raise RuntimeError(f"Spider not found: {spider_name}")
        raise RuntimeError(f"{spider_module} hasn't Spider Module")

    def find_by_request(self, request):
        return []

    def list(self):
        return []

    def _get_spider_path(self, spider_name):
        spider_path = re.search(
            SEP2POINT('.', self.scrapy_module_path) + '\.*(.*)',
            SEP2POINT('.', spider_name)
        ).group(1).replace(".py", "")
        if not spider_path:
            raise RuntimeError("Spider {} Not Found".format(spider_name))
        return spider_path
