# -*- coding: utf-8 -*-
from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = [
        # "http://hd.chinatax.gov.cn/service/getMajorView.do?id=232005",
        "http://hd.chinatax.gov.cn//service/findMajor.do?type=0",  # 自然人
        # "http://hd.chinatax.gov.cn//service/findMajor.do?type=1",  # 法人
    ]

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
