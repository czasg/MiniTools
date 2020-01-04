# -*- coding: utf-8 -*-
import json
import logging
from collections import defaultdict
from minitools import timekiller
from minitools.db.mongodb import get_mongodb_client
from minitools.scrapy import miniSpider
from scrapy import FormRequest, Request
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware

mongodb_client = get_mongodb_client()


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
    mongodb_coll = "city_statistics"
    mongodb_db = "job_lagou"
    cities_statistics = defaultdict(dict)

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
        query_city = self.settings.get("query_city", '武汉|深圳')
        query_keys = self.settings.get("query", 'python')
        self.cities = list(filter(lambda x: x.strip(), query_city.split("|")))
        self.query_keys = list(filter(lambda x: x.strip(), query_keys.split("|")))
        self.query_keys_backup = self.query_keys.copy()
        self.cities_backup = self.cities.copy()
        self.query = self.query_keys.pop()
        yield self.next_city()

    def filling(self):
        if self.query_keys:
            self.query = self.query_keys.pop()
            self.cities = self.cities_backup.copy()
            return self.next_city()

    def next_city(self, city=None):
        try:
            city = city or self.cities.pop()
            self.clear_cookies()
        except:
            self.log(f"{self.query} Cities has exhausted", level=logging.WARNING)
            return self.filling()
        else:
            return Request(f"https://www.lagou.com/jobs/list_{self.query}&city={city}",
                           self.parse_city, meta={"city": city}, dont_filter=True)

    def parse_city(self, response):
        city = response.meta['city']
        form = {
            "first": "true",
            "pn": "1",
            "kd": f"{self.query}",
        }
        referer = f"https://www.lagou.com/jobs/list_{self.query}&city={city}"
        yield FormRequest(f"https://www.lagou.com/jobs/positionAjax.json?px=new"
                          f"&city={city}&needAddtionalResult=false",
                          callback=self.parse_json, formdata=form,
                          meta={"city": city}, headers={"Referer": referer})

    def parse_json(self, response):
        json_data = self.check_response(response)
        if json_data:
            city = response.meta['city']
            count = json_data['content']['positionResult']['totalCount']
            self.log({'query': self.query, city: count})
            self.cities_statistics[self.query].setdefault(city, count)
            yield self.next_city()

    @staticmethod
    def close(spider, reason):
        for query in spider.query_keys_backup:
            statistics = mongodb_client[spider.mongodb_db][f"{spider.mongodb_coll}_{query}"]
            today = int(timekiller.get_today().timestamp())
            doc = dict(
                timestamp=today,
                statistics=json.dumps(spider.cities_statistics[query], ensure_ascii=False),
            )
            statistics.update_one({'timestamp': today}, {"$set": doc}, upsert=True)


if __name__ == '__main__':
    MySpider.run(__file__, suffix="-s query=python|java -s query_city=北京|上海|广州|深圳|杭州|武汉|成都|南京|西安|长沙|天津|东莞")
