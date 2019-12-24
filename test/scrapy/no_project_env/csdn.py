import execjs
from minitools.scrapy import miniSpider
from minitools import current_file_path, search_safe

with open(current_file_path("csdn.js", __file__), 'r') as f:
    anti_spider = execjs.compile(f.read())


class MySpider(miniSpider):
    start_urls = ["https://blog.csdn.net/qq_32969281/article/details/103571605"]
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
    }

    def parse(self, response):
        self.log(response.text)
        arg1 = search_safe("var\s*arg1\s*=\s*'(.*?)'", response.text).group(1)
        acw_sc__v2 = anti_spider.call("anti_csdn", arg1)
        yield response.request.replace(cookies={"acw_sc__v2": acw_sc__v2}, callback=self.parse1)

    def parse1(self, response):
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
