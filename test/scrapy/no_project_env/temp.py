from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["http://sthjj.luan.gov.cn/index.php?keywords=%E5%86%B3%E5%AE%9A%E4%B9%A6&c=search&page=1"]
    custom_settings = {
        "HTTPERROR_ALLOWED_CODES": [403, 412],
        "USER_AGENT":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
    }
    
    def parse(self, response):
        self.log(response.url)
        self.log(response.status)
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
