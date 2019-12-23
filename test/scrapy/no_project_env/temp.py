from minitools.scrapy import miniSpider
from scrapy import Request


class MySpider(miniSpider):
    start_urls = ["https://blog.csdn.net/qq_32969281/article/details/103571605"]
    header = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,und;q=0.8",
        "cache-control": "max-age=0",
        "referer": "https://www.csdn.net/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
    }

    def start_requests(self):
        yield Request(self.start_urls[0], headers=self.header,
                      cookies={"acw_sc__v2": "5e002337b5e3b0617f0dd288f142e9039eb921f8"})

    def parse(self, response):
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
