from minitools.scrapy import miniSpider, from_xpath, xt
from scrapy import FormRequest, Request
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware


#
#
class MySpider(miniSpider):
    start_urls = ["https://www.lagou.com/jobs/allCity.html"]
    # start_urls = ["https://www.lagou.com/jobs/list_python&city=%E5%AE%89%E9%98%B3"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.88 Safari/537.36",
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 8,
        # "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408, 302]
    }

    def parse(self, response):
        for middleware in self.crawler.engine.downloader.middleware.middlewares:
            if isinstance(middleware, CookiesMiddleware):
                middleware.jars[None].clear()
        all_city = response.xpath('//*[@class="word_list"]//li/a')
        count = 0
        for city in all_city:
            city = from_xpath(city, './text()')
            yield Request(f"https://www.lagou.com/jobs/list_python&city={city}",
                          self.parse_city, meta={"city": city, "cookiejar": city})
            if count == 10:
                break
            count += 1
            # break

    def parse_city(self, response):
        city = response.meta['city']
        form = {
            "first": "true",
            "pn": "1",
            "kd": f"python&city={city}"
        }
        yield FormRequest(f"https://www.lagou.com/jobs/positionAjax.json?px=default"
                          f"&city={city}"
                          f"&needAddtionalResult=false",
                          formdata=form, callback=self.parse_json,
                          meta={"cookiejar": city})

    def parse_json(self, response):
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
