from minitools.spider import *


class MySpider(Spider):
    url = 'http://fanyi.youdao.com/'

    def start_requests(self):
        for i in range(10):
            yield Request(self)

    def parse(self, response):
        print('parse')
        self.add_request(Request(self, callback=self.parse2))

    def parse2(self, response):
        print('parse2')


if __name__ == '__main__':
    MySpider.run()
