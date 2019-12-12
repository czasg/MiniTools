from minitools.scrapy import miniSpider
from minitools.scrapy.pipelines import MONGODB_PIPELINE
from minitools import merge_dicts


class MySpider(miniSpider):
    start_urls = ["http://www.baidu.com"]
    custom_settings = merge_dicts(
        MONGODB_PIPELINE
    )

    def parse(self, response):
        for i in range(10):
            yield {"url": "hh", "data": "hei"}


if __name__ == '__main__':
    MySpider.run(__file__)
