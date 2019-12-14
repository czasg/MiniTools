import re
import time
import logging
import requests

from scrapy import Request
from minitools import merge_dicts, timekiller
from minitools.scrapy import miniSpider, from_xpath, xt
from minitools.picture.ziru import ziru
from minitools.scrapy.pipelines import MONGODB_PIPELINE

zr = ziru()
price_list = [0, 21, 42, 64, 85, 107, 128, 149, 171, 192]


class MySpider(miniSpider):
    start_urls = ["http://www.ziroom.com/z/"]
    mongodb = None
    mongodb_client = None
    mongodb_db = "housePrice"
    mongodb_coll = "ziru_zufang"
    custom_settings = merge_dicts(
        MONGODB_PIPELINE,
        {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
            "CONCURRENT_REQUESTS": 1,
            "DOWNLOAD_DELAY": 0.3,
            "mongodb_db": mongodb_db,
            "mongodb_coll": mongodb_coll,
            "mongodb_config": {},
        },
    )

    def parse(self, response):
        cities = []
        select_a = response.xpath('//*[@class="Z_city_list Z_select_body"]/a')
        for a in select_a:
            url = from_xpath(a, './@href', xt.urljoin, source=response)
            city = from_xpath(a, './/text()', xt.string_join)
            cities.append(city)
            yield Request(url, self.parse_city, meta={"city": city}, dont_filter=True)
        self.cities = cities

    def parse_city(self, response):
        city = response.meta['city']
        places = response.xpath('//a[text()="区域"]/following-sibling::div//a')
        for place in places:
            url = from_xpath(place, './@href', xt.urljoin, source=response)
            area_place = from_xpath(place, './text()', xt.string_join)
            house_place = "-".join((city, area_place))
            yield Request(url, self.parse_area, meta={'house_place': house_place, 'city': city},
                          dont_filter=True)

    def parse_area(self, response):
        img_url = re.search('url\((.*?)\)', response.text).group(1)
        house_price_list = zr.get_price(
            requests.get(response.urljoin(img_url)).content
        )

        new = 0
        city = response.meta["city"]
        house_place = response.meta["house_place"]
        houses = response.xpath('//div[@class="Z_list"]/div[@class="Z_list-box"]'
                                '/div[@class="item"][(./div[@class="info-box"])]')

        for house in houses:
            url = from_xpath(house, './div[@class="info-box"]//h5/a/@href', xt.urljoin, source=response)
            if self.mongodb.count({"url": url}):
                continue
            new += 1
            item = {}
            item['url'] = url
            item['city'] = city
            item["house_place"] = house_place
            item["house_name"] = from_xpath(house, './div[@class="info-box"]//h5/a/text()')
            item["house_area"], \
            item["house_floor"] = \
                from_xpath(house, './div[@class="info-box"]/div[@class="desc"]/div[1]/text()').split('|', maxsplit=1)
            item["distance_from_subway"] = \
                from_xpath(house, './div[@class="info-box"]/div[@class="desc"]/div[@class="location"]/text()',
                           xt.string_join)
            item["download_time"] = time.time()

            prices_style = \
                from_xpath(house, './div[@class="info-box"]/div[@class="price"]/span[@class="num"]/@style',
                           xt.extract)
            price = []
            for price_style in prices_style:
                position_num = re.search('position:\s*-(.*?)px', price_style).group(1)
                price.append(house_price_list[price_list.index(int(float(position_num)))])
            item["house_price"] = int(''.join(map(lambda x: str(x), price)))

            yield item

        self.log(f"new item: {new}", level=logging.INFO)
        if new:
            next_page = from_xpath(response, '//a[text()="下一页"]/@href', xt.urljoin)
            yield response.request.replace(url=next_page)

    @staticmethod
    def close(spider, reason):
        statistics = spider.mongodb_client[spider.mongodb_db][f"{spider.mongodb_coll}_statistics"]
        today = int(timekiller.get_today().timestamp())
        doc = dict(
            timestamp=today,
            all_count=spider.mongodb.count({}),
        )
        for city in spider.cities:
            doc[city] = spider.mongodb.count({"city": city})
        statistics.insert_one(doc)


if __name__ == '__main__':
    MySpider.run(__file__)
