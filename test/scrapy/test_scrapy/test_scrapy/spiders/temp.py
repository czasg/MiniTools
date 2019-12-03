# -*- coding: utf-8 -*-
from minitools.scrapy import miniSpider
from scrapy import Request

class MySpider(miniSpider):
    start_urls = ['http://www.nujiang.gov.cn/nj/72913014084337664/20191106/323412.html']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, encoding='gb2312')

    def parse(self, response):
        print(response.encoding)
        print(response.text)

    @classmethod
    def update_settings(cls, settings):
        custom_settings = {
            'FEED_EXPORT_ENCODING': 'gb2312'
        }
        settings.setdict(custom_settings, priority='spider')


if __name__ == '__main__':
    MySpider.run(__file__)
