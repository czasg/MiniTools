from minitools.spider.thread_spider import *


class MySpider(Spider):
    url = 'https://www.cnblogs.com/mswei/p/9835370.html'
    coding = None
    def start_requests(self):
        yield Request(self)

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    MySpider.run()

# todo, 下载或解析过程中，遇到报错就无法终止程序
