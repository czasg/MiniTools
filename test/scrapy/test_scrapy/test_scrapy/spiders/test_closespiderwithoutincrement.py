from minitools.scrapy import miniSpider
from minitools.scrapy.extensions import close_spider_without_increment
from minitools import merge_dict


class MySpider(miniSpider):
    name = "test_closespider"
    start_urls = ["https://www.baidu.com/s?ie=UTF-8&wd=%E7%88%AC%E8%99%AB%E5%A4%A7%E9%87%8F%E8%A3%81%E5%91%98"]
    custom_settings = merge_dict(
        close_spider_without_increment,
        {'CLOSESPIDER_CHECKINTERVAL': '10'}
    )

    def parse(self, response):
        import time
        time.sleep(20)
        print(response.url)


if __name__ == '__main__':
    MySpider.run(__file__)
