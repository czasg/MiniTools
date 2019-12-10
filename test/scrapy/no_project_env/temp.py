from minitools.scrapy import miniSpider
from minitools.scrapy import refresh_response


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)

    # import subprocess
    #
    # subprocess.call(f"scrapy runspider {__file__}")
