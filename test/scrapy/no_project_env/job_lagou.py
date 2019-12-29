# -*- coding: utf-8 -*-
import json
import logging
from minitools.scrapy import miniSpider, from_xpath
from scrapy import FormRequest, Request
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware

area = {
    '11': '北京',
    '12': '天津',
    '13': '河北',
    '14': '山西',
    '15': '内蒙古',
    '21': '辽宁',
    '22': '吉林',
    '23': '黑龙江',
    '31': '上海',
    '32': '江苏',
    '33': '浙江',
    '34': '安徽',
    '35': '福建',
    '36': '江西',
    '37': '山东',
    '41': '河南',
    '42': '湖北',
    '43': '湖南',
    '44': '广东',
    '45': '广西',
    '46': '海南',
    '50': '重庆',
    '51': '四川',
    '52': '贵州',
    '53': '云南',
    '54': '西藏',
    '61': '陕西',
    '62': '甘肃',
    '63': '青海',
    '64': '宁夏',
    '65': '新疆',
    '71': '台湾',
    '81': '香港',
    '82': '澳门',
}


class MySpider(miniSpider):
    start_urls = ["https://www.lagou.com/jobs/allCity.html"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.88 Safari/537.36",
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
    }
    collect_url = "https://a.lagou.com/collect"
    cookies_middleware = None

    def check_response(self, response):
        try:
            return json.loads(response.text)
        except:
            self.log(response.text, level=logging.ERROR)
            return {}

    def clear_cookies(self):
        if not self.cookies_middleware:
            for middleware in self.crawler.engine.downloader.middleware.middlewares:
                if isinstance(middleware, CookiesMiddleware):
                    self.cookies_middleware = middleware
        self.cookies_middleware.jars.clear()

    def start_requests(self):
        # yield Request(self.start_urls[0], meta={"dont_merge_cookies": True})
        self.cities = list(area.values())
        yield self.next_city()

    # def parse(self, response):
    #     all_city = response.xpath('//*[@class="word_list"]//li/a')
    #     self.cities = [from_xpath(city, './text()') for city in all_city]
    #     yield self.next_city()

    def next_city(self, city=None):
        try:
            city = city or self.cities.pop()
            self.clear_cookies()
        except:
            self.log("Cities has exhausted", level=logging.WARNING)
        else:
            return Request(f"https://www.lagou.com/jobs/list_python&city={city}",
                           self.parse_city, meta={"city": city}, dont_filter=True)

    def parse_city(self, response):
        city = response.meta['city']
        form = {
            "first": "true",
            "pn": "1",
            "kd": f"python&city={city}"
        }
        referer = f"https://www.lagou.com/jobs/list_python&city={city}"
        yield FormRequest(f"https://www.lagou.com/jobs/positionAjax.json?px=default"
                          f"&city={city}&needAddtionalResult=false",
                          callback=self.parse_json, formdata=form,
                          meta={"city": city}, headers={"Referer": referer})

    def parse_json(self, response):
        json_data = self.check_response(response)
        if json_data:
            self.log({response.meta['city']: json_data['content']['positionResult']['totalCount']})
            yield self.next_city()


if __name__ == '__main__':
    MySpider.run(__file__)
