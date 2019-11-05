from minitools.spider.thread_spider import *


class MySpider(Spider):
    url = 'http://fanyi.youdao.com/'

    def start_requests(self):
        for i in range(10):
            yield Request(self)

    def parse(self, response):
        print(response.url)
        yield Request(self, callback=self.parse2)

    def parse2(self, response):
        print(response.url)


if __name__ == '__main__':
    MySpider.run()
