from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["http://www.baidu.com"]

    def parse(self, response):
        print("Hello world")


if __name__ == '__main__':
    import os

    MySpider.run(__file__, log_path=os.path.dirname(__file__))
