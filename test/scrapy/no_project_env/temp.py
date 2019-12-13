from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://github.com/CzaOrz"]

    def parse(self, response):
        self.log(response.url)
        self.log(response.status)


if __name__ == '__main__':
    MySpider.run(__file__)
