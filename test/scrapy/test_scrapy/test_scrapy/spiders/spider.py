from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    name = "test_fast"
    start_urls = ['http://www.czasg.xyz']

    def parse(self, response):
        print(response.url)


if __name__ == '__main__':
    MySpider.run(__file__)
