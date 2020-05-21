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
    name = "美团外卖"
    dbName = "商城类"
    collName = "美团外卖"
    cat = "零碎任务"
    website_name = "美团外卖"
    website_url = "https://www.meituan.com/"

    url = "https://wh.meituan.com/s/{}/"
    license_uri = "https://www.meituan.com/meishi/api/poi/getFoodSafetyDetail"
    search_all_store_uri = "https://www.meituan.com/meishi/{}/"
    tempGoodsSet = set()
    tempStoreSet = set()
    storesNewBool = False
    page = 1

    custom_settings = csp.ll_extra_settings(
        {
            "DOWNLOAD_DELAY": 1.5,
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        },
        {"DOWNLOADER_MIDDLEWARES": {"scrapyProj.middlewares.RotateUserAgentMiddleware": None}}
    )

    def start_requests(self):
        self.searchAll = False
        self.searchKey = self.crawler.settings.get("target")
        if not self.searchKey:
            raise Exception("未指定搜索关键词")
        self.log("获取到店铺名称: {}".format(self.searchKey))
        if self.searchKey == "https://wh.meituan.com/meishi/":
            self.searchAll = True

        self.goodsColl = self.client[self.dbName][self.collName + "(商品信息)"]
        self.storesColl = self.client[self.dbName][self.collName + "(店铺信息)"]
        self.emptySearchColl = self.client[self.dbName]["空查询"]
        if self.emptySearchColl.count({"type": self.collName, "key": self.searchKey}):
            return self.log("查询结果为空，爬虫结束".format(self.searchKey), logging.ERROR)
        yield Request(self.website_url, self.patchCookie)

    def patchCookie(self, response):
        if self.searchAll:
            yield Request(self.searchKey + 'pn{}/'.format(self.page), self.parseMeiShi)
        else:
            yield Request(self.url.format(self.searchKey))

    def parseMeiShi(self, response):
        try:
            appData = rea.search('window._appState\s*=\s*({.*?});\s*</script>', response.text, re.S).group(1)
            appData = json.loads(appData)
            stores = appData["poiLists"]["poiInfos"]
        except:
            return self.log("页面改版，没有获取到主体列表", logging.ERROR)
        goodsNew = storesNew = 0
        for store in stores:
            storeName = store.get('title', '')
            storeId = str(store.get('poiId', ''))
            if not storeId:
                continue
            if storeId not in self.tempStoreSet:
                self.tempStoreSet.add(storeId)
                if self.storesColl.count({"店铺ID": storeId}):
                    continue
                # if storesNew > 3: continue
                storesNew += 1
                storeUrl = self.search_all_store_uri.format(storeId)
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
                # 图片链接
                picUri = store.get("frontImg", "")
                if picUri:
                    base64img = img2base64(picUri)
                    if base64img != "data:image/png;base64,":
                        document["店铺首页截图"].append(Image({
                            "url": picUri,
                            "base64": base64img
                        }))
                # 店铺动态评分
                document["店铺动态评分"]["平均评分"] = store.get("avgScore", "")
                # 企业资质
                document["企业资质"]["店铺地址"] = store.get("address", "")
                yield FormRequest(self.license_uri, self.parseLicense, formdata={
                    "poiId": storeId
                }, meta={
                    "document": document
                })
        self.log("店铺信息: 共{}条其中{}条未爬".format(len(stores), storesNew), logging.INFO)
        if storesNew:
            self.page += 1
            yield Request(self.searchKey + 'pn{}/'.format(self.page), self.parseMeiShi)

    def parse(self, response):
        if "页面暂时无法访问" in response.text:
            return self.log("出现反爬，返回404页面", logging.ERROR)
        if "没有符合条件的商家" in response.text:
            self.emptySearchColl.insert_one({"type": self.collName, "key": self.searchKey})
            return self.log("未查询商家，记录到空查询", logging.ERROR)

        storesInfo = {}
        try:
            appData = rea.search('window.AppData\s*=\s*({.*?});\s*</script>', response.text, re.S).group(1)
            appData = json.loads(appData)
            data = appData["data"]["searchResult"]
            for store in data:
                storesInfo[str(store['id'])] = deepcopy(store)
        except:
            return self.log("页面改版，没有获取到主体列表", logging.ERROR)
        goodsNew = storesNew = 0
        stores = response.xpath('//*[@class="common-list-main"]/div')
        for store in stores:
            storeName = xpath(store, './div[@class="default-card"]//div[@class="list-item-desc"]/div/a/text()')
            storeUrl = xpath(store, './div[@class="default-card"]/div/a/@href')
            if not storeUrl:
                continue
            storeUrl = response.urljoin(storeUrl)
            storeId = rea.search('.*?/(\d+?)/', storeUrl).group(1)
            if not storeId:
                continue
            if storeId not in self.tempStoreSet:
                self.tempStoreSet.add(storeId)
                if self.storesColl.count({"店铺ID": storeId}):
                    continue
                if storesNew > 3: continue
                storesNew += 1
                detailInfo = storesInfo.get(storeId)
                if not detailInfo:
                    continue
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
                # 图片链接
                picUri = detailInfo.get("imageUrl", "")
                picUri = re.sub('(https?://.*?)/.*?/(.*)', '\\1/\\2', picUri)
                if picUri:
                    base64img = img2base64(picUri)
                    if base64img != "data:image/png;base64,":
                        document["店铺首页截图"].append(Image({
                            "url": picUri,
                            "base64": base64img
                        }))
                # 店铺动态评分
                document["店铺动态评分"]["平均评分"] = detailInfo.get("avgscore", "")
                # 店铺标签
                document["店铺标签"] = detailInfo.get("backCateName", "")
                # 企业资质
                document["企业资质"]["店铺地址"] = detailInfo.get("address", "")
                yield FormRequest(self.license_uri, self.parseLicense, formdata={
                    "poiId": storeId
                }, priority=1, meta={
                    "document": document
                })
        self.log("店铺信息: 共{}条其中{}条未爬".format(len(stores), storesNew), logging.INFO)

    def parseLicense(self, response):
        document = response.meta["document"]
        try:
            appData = json.loads(response.text)["data"]
        except:
            return self.log("证书接口改版，返回非json", logging.ERROR)
        document["企业资质"]["管理等级"] = appData.get("level", "")
        document["企业资质"]["单位名称"] = appData.get("name", "")
        document["企业资质"]["许可证号"] = appData.get("licenseNo", "")
        document["企业资质"]["法定代表人"] = appData.get("legalRepresentative", "")
        document["企业资质"]["经营地址"] = appData.get("address", "")
        document["企业资质"]["有效期"] = appData.get("validDate", "")
        # 营业执照
        picUri = appData.get("businessLicenceImgUrl")
        if picUri:
            base64img = img2base64(picUri)
            if base64img != "data:image/png;base64,":
                document["证件截图"].append(Image({
                    "url": picUri,
                    "base64": img2base64(picUri),
                    "licenseType": "营业执照"
                }))
        # 餐饮服务许可证
        picUri = appData.get("restaurantLicenceImgUrl")
        if picUri:
            base64img = img2base64(picUri)
            if base64img != "data:image/png;base64,":
                document["证件截图"].append(Image({
                    "url": picUri,
                    "base64": img2base64(picUri),
                    "licenseType": "餐饮服务许可证"
                }))
        Store(document).save(self.storesColl)


if __name__ == '__main__':
    MySpider.run_download(suffix="-s target=https://wh.meituan.com/meishi/ --loglevel=DEBUG", fast=__file__)
