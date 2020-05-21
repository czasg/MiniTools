import time
import base64
import logging
import requests
import datetime

from scrapyProj.basespiders.shortcut import LLBaseSpider
from scrapyProj.tools import *
from scrapyProj.candy.商城类.data import Store, Good, Image
from copy import deepcopy


def img2base64(img):
    if isinstance(img, str) and img.startswith("http"):
        time.sleep(0.5)  # 图片下载加上时延
        img = requests.get(img).content
    if isinstance(img, bytes):
        img = base64.b64encode(img).decode()
    if not isinstance(img, str):
        raise Exception("不支持 {} 格式的图片".format(type(img)))
    return "data:image/png;base64," + img


class MySpider(LLBaseSpider):
    name = "卷皮商城"
    dbName = "商城类"
    collName = "卷皮商城"
    cat = "零碎任务"
    website_name = "卷皮商城"
    website_url = "http://www.juanpi.com/"

    url = "http://www.juanpi.com/search?keywords={}"
    license_uri = "http://www.juanpi.com/license/viewlicense"
    food_license_uri = "http://www.juanpi.com/license/viewFoodLicense"
    tempGoodsSet = set()
    tempStoreSet = set()

    custom_settings = csp.ll_extra_settings(
        {
            "DOWNLOAD_DELAY": 1.5,
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        },
        {"DOWNLOADER_MIDDLEWARES": {"scrapyProj.middlewares.RotateUserAgentMiddleware": None}}
    )

    def start_requests(self):
        self.searchKey = self.crawler.settings.get("target")
        if not self.searchKey:
            raise Exception("未指定搜索关键词")
        self.log("获取到店铺名称: {}".format(self.searchKey))

        self.goodsColl = self.client[self.dbName][self.collName + "(商品信息)"]
        self.storesColl = self.client[self.dbName][self.collName + "(店铺信息)"]
        self.emptySearchColl = self.client[self.dbName]["空查询"]
        if self.emptySearchColl.count({"type": self.collName, "key": self.searchKey}):
            return self.log("查询结果为空，爬虫结束".format(self.searchKey), logging.ERROR)
        # yield Request(self.website_url, self.patchCookie)
        yield Request(self.url.format(self.searchKey))

    def parse(self, response):
        stores = response.xpath('//*[contains(@class, "goods-list")]/li')
        for store in stores:
            storeUrl = xpath(store, './/div[@class="pic-img"]/a/@href')
            storeId = rea.search('.*/(\d+)$', storeUrl).group(1)
            if not storeId:
                continue
            if storeId not in self.tempStoreSet:
                self.tempStoreSet.add(storeId)
                storeUrl = response.urljoin(storeUrl)
                document = {
                    "店铺名称": "",
                    "店铺网址": storeUrl,
                    "店铺首页截图": [],
                    "店铺类别": "",
                    "所在地": "",
                    "证件截图": [],
                    "企业资质": dict(),
                    "店铺标签": "",
                    "店铺动态评分": dict(),
                    "下载时间": datetime.datetime.now(),
                    "店铺ID": storeId
                }
                yield Request(storeUrl, self.parseDetail, meta={"document": document})
            break

    def parseDetail(self, response):
        document = response.meta['document']
        licenseUrl = xpath(response, '//*[@class="sale_license sale-line"]/a/@href')
        document["店铺名称"] = xpath(response, '//*[@class="sale_name"]/text()')
        if not licenseUrl:
            return self.log('该店铺没有营业执照或者页面改版了: {}'.format(document["店铺网址"]), logging.ERROR)
        licenseId = rea.search('.*?/(\d+)$', licenseUrl).group(1)
        if not licenseId:
            return self.log('证书页面改版，id没了: {}'.format(document["店铺网址"]), logging.ERROR)
        yield FormRequest(self.license_uri, formdata={"seller": licenseId}, callback=self.getLicense, meta={
            "licenseId": licenseId,
            "document": document
        })

    def getLicense(self, response):
        document = response.meta['document']
        licenseId = response.meta['licenseId']
        for picUri in response.xpath('//*[@class="main"]//img/@src').extract():
            picUri = response.urljoin(picUri)
            base64img = img2base64(picUri)
            if base64img == "data:image/png;base64,":
                pass
            else:
                document["证件截图"].append(Image({
                    "url": picUri,
                    "base64": base64img,
                    "licenseType": "营业执照"
                }))
        # yield FormRequest(self.food_license_uri, formdata={"seller": licenseId}, callback=self.getFoodsLicense, meta={
        #     "licenseId": licenseId,
        #     "document": document
        # })
        from pprint import pprint
        pprint(document)
        Store(document).save(self.storesColl)

    def getFoodsLicense(self, response):
        document = response.meta['document']
        for picUri in response.xpath('//*[@class="main"]//img/@src').extract():
            picUri = response.urljoin(picUri)
            base64img = img2base64(picUri)
            if base64img == "data:image/png;base64,":
                pass
            else:
                document["证件截图"].append(Image({
                    "url": picUri,
                    "base64": base64img,
                    "licenseType": "食品许可证"
                }))
        Store(document).save(self.storesColl)


if __name__ == '__main__':
    MySpider.run_download(suffix="-s target=母婴 --loglevel=DEBUG", fast=__file__)
