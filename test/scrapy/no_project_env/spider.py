from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com/"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "HTTPERROR_ALLOWED_CODES": [521],
    }

    def parse(self, response):
        for i in range(10):
            yield {'cza': 'cza', 'is': 'is', 'sg': '哈哈'}  # Request, BaseItem, dict or None
        yield response.request.replace(dont_filter=True, callback=self.parse1)

    def parse1(self, response):
        # self.crawler.engine.close_spider(self, 'just/for/test')
        print("this is parse1")


if __name__ == '__main__':
    import os

    MySpider.run(__file__, suffix=f"-s JOBDIR={os.path.dirname(__file__)}")
