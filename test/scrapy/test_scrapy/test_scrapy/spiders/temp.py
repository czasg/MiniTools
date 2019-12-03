# -*- coding: utf-8 -*-
from minitools.scrapy import miniSpider, refresh_encoding
from scrapy import Request


class MySpider(miniSpider):
    start_urls = ['http://www.nujiang.gov.cn/nj/72913014084337664/20191106/323412.html']  # 这个乱码可太嫌人了

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)  # ISO-8859-1 gb2312

    def parse(self, response):
        # response = refresh_encoding(response)
        # print(response.text)
        response.replace(encoding='utf-8')
        print(response.encoding)
        print(response.text)



if __name__ == '__main__':
    MySpider.run(__file__)
