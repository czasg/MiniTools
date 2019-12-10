from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        for i in range(10):
            yield {'cza': 'cza', 'is': 'is', 'sg': '哈哈'}  # Request, BaseItem, dict or None


if __name__ == '__main__':
    MySpider.run(__file__, save=True)
