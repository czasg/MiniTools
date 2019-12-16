from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com/"]

    def parse(self, response):
        for _ in range(10):
            yield {"key": "value", "test-key": "test-value"}


if __name__ == '__main__':
    MySpider.run(__file__, save=True)
