# -*- coding: utf-8 -*-
from minitools.scrapy import miniSpider
from minitools.scrapy.downloadermiddlewares import \
    PROXY_RETRY_MIDDLEWARE, \
    PROXY_POOL_RETRY_MIDDLEWARE, \
    FIXED_PROXY_MIDDLEWARE, \
    FIXED_PROXY_POOL_RETRY_MIDDLEWARE, \
    FIXED_PROXY_RETRY_MIDDLEWARE
from minitools import get_proxy
from scrapy import Request


class MySpider(miniSpider):
    # start_urls = ['http://www.czasg.xyz']
    start_urls = ['http://www.czasgcza000.xyz', 'http://www.czasgcza111.xyz',
                  'http://www.czasgcza222.xyz', 'http://www.czasgcza333.xyz']
    get_proxy = staticmethod(get_proxy)

    def start_requests(self):
        self.mini_proxy = "36.104.132.31:3128"
        for url in self.start_urls:
            yield Request(url, headers={'Cookie': 'anti_spider=True;'})

    def parse(self, response):
        print(response.url)

    # @classmethod
    # def check_logger_files(cls):
    #     return super().check_logger_files(expires=1)

    @classmethod
    def update_settings(cls, settings):
        custom_settings = FIXED_PROXY_POOL_RETRY_MIDDLEWARE
        custom_settings['RETRY_TIMES'] = 3
        custom_settings['RETRY_HTTP_CODES'] = [500, 502, 503, 504, 522, 524, 408, 404, 403]
        settings.setdict(custom_settings, priority='spider')


if __name__ == '__main__':
    MySpider.run(__file__)
