from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.csdn.net/"]
    
    def parse(self, response):
        self.log(response.url)
        self.log(response.status)
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
