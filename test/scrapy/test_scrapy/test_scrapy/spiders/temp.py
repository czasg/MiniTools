from minitools.scrapy import miniSpider
from minitools.scrapy.downloadermiddlewares import PROXY_RETRY_MIDDLEWARE
from scrapy import Request


class MySpider(miniSpider):
    start_urls = ['http://www.czasg.xyz']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers={'Cookie': 'anti_spider=True;'})

    def parse(self, response):
        # print(response.headers['Set-Cookie'])
        print(response.url)
        # yield response.request.replace(callback=self.parse1, dont_filter=True)
        # yield Request('http://www.czczczczczczc.com')

    # @classmethod
    # def check_logger_files(cls):
    #     return super().check_logger_files(expires=1)

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(PROXY_RETRY_MIDDLEWARE, priority='spider')


if __name__ == '__main__':
    MySpider.run(__file__)
