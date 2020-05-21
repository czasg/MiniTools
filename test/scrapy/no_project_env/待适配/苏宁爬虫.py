import uuid
import time
import base64
import logging
import requests
import datetime

from scrapyProj.basespiders.shortcut import LLBaseSpider
from scrapyProj.tools import *
from scrapyProj.tools.captcha import get_code_from_captcha
from scrapyProj.candy.商城类.data import Store, Good, Image


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
    name = "苏宁易购"
    dbName = "商城类"
    collName = "苏宁易购"
    cat = "零碎任务"
    website_name = "苏宁易购"
    website_url = "https://www.suning.com"

    uri = "https://search.suning.com/{}/"
    search_uri = "https://search.suning.com/emall/searchV1Product.do?keyword={}&pg=01&paging=1&sesab=FCAABBABCAAA&id=IDENTIFYING"
    license_uri = "https://shop.suning.com/{}/showLicence.html"  # 证书页面
    license_ajax = "https://shop.suning.com/ajax/showLicenceInfo.do"  # 证书接口
    captcha_uri = "https://vcs.suning.com/vcs/imageCode.htm?uuid="
    star_uri = "https://yibupi.suning.com/jsonp/{}/shopinfo/shopinfo.html?callback=shopinfo"  # 店铺评分
    tempGoodsSet = set()
    tempStoreSet = set()

    custom_settings = csp.ll_extra_settings(
        {
            "DOWNLOAD_DELAY": 1.5,
        }
    )

    def start_requests(self):
        self.searchKey = self.crawler.settings.get("target")
        self.allowGoods = False
        if not self.searchKey:
            raise Exception("未指定搜索关键词")
        if self.searchKey.startswith('goods:'):
            self.allowGoods = True
            self.searchKey = self.searchKey.replace('goods:', '')

        self.goodsColl = self.client[self.dbName][self.collName + "(商品信息)"]
        self.storesColl = self.client[self.dbName][self.collName + "(店铺信息)"]
        self.emptySearchColl = self.client[self.dbName]["空查询"]

        if self.emptySearchColl.count({"type": self.collName, "key": self.searchKey}):
            return self.log("查询结果为空，爬虫结束".format(self.searchKey), logging.ERROR)
        # if self.allowGoods:  # 商品
        #     self.spiderproxy = get_wan_proxy(p=0.6)
        yield Request(self.uri.format(self.searchKey), callback=self.patchCookies)

    def patchCookies(self, response):  # 需要先跳转搜索页拿cookies
        search_uri = self.search_uri.format(self.searchKey)
        yield Request(search_uri)

    def captchaRequest(self, storeId, tryCount=0, document=None):
        """
        :param storeId: 店铺id
        :param tryCount: 验证码重试次数
        :return:
        """
        if tryCount > 5: return
        captcha_uuid = str(uuid.uuid4())
        return Request(self.captcha_uri + captcha_uuid, self.validCaptcha, priority=1, meta={
            "storeId": storeId,
            "dont_merge_cookies": True,
            "tryCount": tryCount,
            "document": document or {},
            "captcha_uuid": captcha_uuid
        }, dont_filter=True)

    def parse(self, response):
        if "没有找到相关商品" in response.text:
            self.log("此次查询已记录为异常：`{}` 查询结果为空，直接返回".format(self.searchKey), logging.ERROR)
            return self.emptySearchColl.insert_one({"type": self.collName, "key": self.searchKey})

        goodsNew = storesNew = 0
        stores = response.xpath('//li')
        for store in stores:
            # 店铺链接
            storeUrl = xpath(store, './/a[@class="store-name"]/@href')
            if not storeUrl:
                continue
            storeUrl = response.urljoin(storeUrl)
            try:
                storeData = eval(xpath(store, './/a[@class="store-name"]/@sa-data'))
                storeId = storeData["shopid"]
            except:
                self.log("苏宁商品列表页可能改版了", logging.ERROR)
                continue
            if not storeId:
                continue
            goodsUrl = xpath(store, './/*[@class="img-block"]/a/@href')
            if not goodsUrl:
                continue
            goodsUrl = response.urljoin(goodsUrl)

            title = xpath(store, './/*[@class="title-selling-point"]/a/@title')
            content = wenben(store, './/*[@class="title-selling-point"]')
            storeName = xpath(store, './/a[@class="store-name"]/text()')

            if self.allowGoods and goodsUrl not in self.tempGoodsSet:
                if goodsNew > 9: continue
                self.tempGoodsSet.add(goodsUrl)
                if not self.goodsColl.count({"商品网址": goodsUrl}):
                    document = {
                        "商品名称": title,
                        "商品网址": goodsUrl,
                        "商品描述": content,
                        "商品首页截图": [],
                        "宣传图片": [],
                        "商品类别": "",
                        "店铺名称": storeName,
                        "店铺网址": storeUrl,
                        "下载时间": datetime.datetime.now(),
                        "店铺ID": storeId,
                        "售后信息": {
                            "说明": [],
                            "更多说明": []
                        },
                        "详情信息": {
                            "商品详情": dict(),
                        }
                    }
                    for picUri in store.xpath('.//*[@class="res-img"]/div[@class="img-block"]/a/img/@src').extract():
                        if picUri and picUri.startswith("/"):
                            picUri = response.urljoin(picUri)
                            document["宣传图片"].append(Image({
                                "url": picUri,
                                "base64": img2base64(picUri)
                            }))
                    yield Request(
                        goodsUrl,
                        callback=self.goodsPageParse,
                        priority=1,
                        meta={
                            "document": document
                        }
                    )
                    goodsNew += 1
            if storeId not in self.tempStoreSet:
                if self.allowGoods: continue
                self.tempStoreSet.add(storeId)
                if not self.storesColl.count({"店铺ID": storeId}):
                    document = {
                        "店铺名称": storeName,
                        "店铺网址": storeUrl,
                        "店铺首页截图": [],
                        "店铺类别": "",
                        "所在地": "",
                        "证件截图": [],
                        "企业资质": dict(),
                        "店铺标签": "",
                        "店铺动态评分": dict(),
                        "下载时间": datetime.datetime.now(),
                        "店铺ID": storeId,
                        "开店信息": dict()
                    }
                    yield self.captchaRequest(storeId, document=document)
                    storesNew += 1
        scanned_printer(self, stores, storesNew)

    def goodsPageParse(self, response):
        """
        商品页面解析
        :param response:
        :return:
        """
        document = response.meta["document"]

        # 详情信息-商品详情
        for goodsInfo in response.xpath('//*[@class="prod-detail-container"]//li'):
            key, value = rea.search('(.*?)[:：](.*)', jxpath(goodsInfo, './/text()'), re.S).groups()
            if all((key, value)):
                document["详情信息"]["商品详情"][key.strip()] = value.strip()

        for goodsParam in response.xpath('//*[@id="J-procon-param"]//tr'):
            tds = goodsParam.xpath('./td')
            if len(tds) < 2:
                continue
            key, value = jxpath(tds[0], './/text()'), jxpath(tds[1], './/text()')
            if all((key, value)):
                document["详情信息"]["商品详情"][key] = value

        for picUri in re.findall('<img onload=".*?src.?="(.*?)"', response.text):
            if picUri:
                picUri = response.urljoin(picUri)
                document["宣传图片"].append(Image({
                    "url": picUri,
                    "base64": img2base64(picUri)
                }))
        Good(document).save(self.goodsColl)

    def validCaptcha(self, response):
        """
        验证码识别
        :param response:
        :return:
        """
        storeId = response.meta["storeId"]
        tryCount = response.meta["tryCount"]
        document = response.meta["document"]
        captcha_uuid = response.meta["captcha_uuid"]
        yield FormRequest(
            self.license_ajax,
            formdata={
                "shopID": storeId,
                "uuid": captcha_uuid,
                "code": get_code_from_captcha(response.body, model="suning_v1", log=False)
            },
            meta={
                "storeId": storeId,
                "tryCount": tryCount,
                "document": document,
            },
            priority=2,
            callback=self.parseLicense
        )

    def parseLicense(self, response):
        storeId = response.meta["storeId"]
        tryCount = response.meta["tryCount"]
        document = response.meta["document"]
        try:
            starInfo = requests.get(self.star_uri.format(storeId)).text
            starInfo = re.search('.*?({.*?})', starInfo).group(1)
            starInfo = json.loads(starInfo)
            document["店铺动态评分"]["用户评价"] = starInfo.get("Qstar", "")
            document["店铺动态评分"]["物流时效"] = starInfo.get("Astar", "")
            document["店铺动态评分"]["售后服务"] = starInfo.get("Dstar", "")
            document["店铺动态评分"]["用户评价-高于同行"] = starInfo.get("Qpercent", "")
            document["店铺动态评分"]["物流时效-高于同行"] = starInfo.get("Apercent", "")
            document["店铺动态评分"]["售后服务-高于同行"] = starInfo.get("Dpercent", "")
            document["企业资质"]["客服电话"] = starInfo.get("telPhone", "")
            document["企业资质"]["公司名称"] = starInfo.get("companyName", "")
            document["企业资质"]["国家"] = starInfo.get("countryName", "")
            document["企业资质"]["省"] = starInfo.get("companyProvince", "")
            document["企业资质"]["城市"] = starInfo.get("companyCity", "")
            document["企业资质"]["地址"] = starInfo.get("companyAddress", "")
        except:
            pass
        picUri = rea.search('^"(.*)"$', response.text).group(1)
        if picUri:
            picUri = response.urljoin(picUri)
            document["证件截图"].append(Image({
                "url": picUri,
                "base64": img2base64(picUri)
            }))
            Store(document).save(self.storesColl)
        else:
            self.log("验证码失败或改版...重试: {} storeId: {}".format(tryCount, storeId), logging.WARNING)
            yield self.captchaRequest(storeId, tryCount + 1, document=document)


if __name__ == '__main__':
    MySpider.run_download(suffix="-s target=小米10 --loglevel=DEBUG", fast=__file__)
