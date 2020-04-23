import re
import logging
import requests
import datetime
from copy import deepcopy
from minitools.scrapy import miniSpider, next_page_request
from scrapy import Request, FormRequest
from minitools import *


def img2base64(img):
    if isinstance(img, str) and img.startswith("http"):
        img = requests.get(img).content
    if isinstance(img, bytes):
        img = base64img.byte2base64(img)
    if not isinstance(img, str):
        raise Exception("不支持 {} 格式的图片".format(type(img)))
    return "data:image/png;base64," + img


def captcha(img):
    if isinstance(img, bytes):
        img = base64img.byte2base64(img)
    return img


class MySpider(miniSpider):
    name = "京东商城"
    url = "https://search.jd.com/Search?keyword={}&enc=utf-8&pvid=adc505dac9d2429a95b6da44b7575ead"
    captcha_uri = "https://mall.jd.com/sys/vc/createVerifyCode.html"
    cross_captcha_uri = "https://mall.jd.hk/sys/vc/createVerifyCode.html"
    license_uri = "https://mall.jd.com/showLicence-{}.html"
    search_uri = "https://search.jd.com/s_new.php?keyword={}&enc=utf-8&page=1"  # 第二页开始
    instru_uri = "https://c0.3.cn/stock?skuId={}&venderId={}&callback=jQuery9683234&cat={}&area=17_1381_50718_0"  # 说明链接
    score_uri = "https://mall.jd.com/view/getJshopHeader.html?callback=jQuery4335455&appId={}"
    tempGoodsSet = set()
    tempStoreSet = set()

    custom_settings = {
        "DOWNLOAD_DELAY": 1.5,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }

    def start_requests(self):
        self.searchKey = self.crawler.settings.get("target")
        if not self.searchKey:
            raise Exception("未指定搜索关键词")

        yield Request(self.url.format(self.searchKey), callback=self.patchCookies)

    def patchCookies(self, response):  # 需要先跳转搜索页拿cookies
        search_uri = self.search_uri.format(self.searchKey)
        yield Request(search_uri)

    def captchaRequest(self, storeId, tryCount=0, document=None or {}, uri=None):
        """
        :param storeId: 店铺id
        :param tryCount: 验证码重试次数
        :return:
        """
        if tryCount > 5: return
        return Request(uri or self.captcha_uri, self.validCaptcha, priority=1, meta={
            "storeId": storeId,
            "dont_merge_cookies": True,
            "tryCount": tryCount,
            "document": deepcopy(document)
        }, dont_filter=True)

    def parse(self, response):
        goodsNew = storesNew = 0
        stores = response.xpath('//*[@id="J_goodsList"]//li[@class="gl-item"]')
        for store in stores:
            storeUrl = from_xpath(store, './/*[@class="p-shop"]//a/@href')
            if not storeUrl:
                continue
            storeUrl = response.urljoin(storeUrl)
            storeId = re.search('index-(\d+)\.html', storeUrl)
            if not storeId:
                continue
            storeId = storeId.group(1)
            goodsUrl = from_xpath(store, './/*[@class="p-img"]/a/@href')
            if not goodsUrl:
                continue
            goodsUrl = response.urljoin(goodsUrl)
            title = from_xpath(store, './/*[@class="p-img"]/a/@title')
            content = from_xpath(store, './/*[@class="p-name p-name-type-2"]', type=xt.analysis_article)
            storeName = from_xpath(store, './/*[@class="p-shop"]//a/text()')

            if goodsUrl not in self.tempGoodsSet:
                self.tempGoodsSet.add(storeId)
                image = []
                for img in store.xpath('.//*[@class="ps-main" or @class="p-img"]//img'):  # 两种不同的页面结构
                    picUri = from_xpath(img, './/@data-lazy-img|.//@source-data-lazy-img')
                    if picUri:
                        picUri = response.urljoin(picUri)
                        image.append(img2base64(picUri))
                yield Request(goodsUrl, callback=self.goodsPageParse, priority=1, meta={
                    "document": {
                        "商品名称": title,
                        "商品网址": goodsUrl,
                        "商品描述": content,
                        "商品首页截图": None,
                        "宣传图片": image,
                        "商品类别": None,
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
                })
                goodsNew += 1
            if storeId not in self.tempStoreSet:
                self.tempStoreSet.add(storeId)
                document = {
                    "店铺名称": storeName,
                    "店铺网址": storeUrl,
                    "店铺首页截图": None,
                    "店铺类别": None,
                    "所在地": None,
                    "企业资质": {
                        "证件截图": []
                    },
                    "店铺标签": None,
                    "店铺动态评分": dict(),
                    "下载时间": datetime.datetime.now(),
                    "店铺ID": storeId
                }
                yield self.captchaRequest(storeId, document=document)
                storesNew += 1
        self.log("商品信息: 共{}条其中{}条未爬".format(len(stores), goodsNew), logging.INFO)
        self.log("店铺信息: 共{}条其中{}条未爬".format(len(stores), storesNew), logging.INFO)
        if goodsNew or storesNew:
            yield next_page_request(response, "page=(\d+)")

    def goodsPageParse(self, response):
        document = response.meta["document"]

        # 售后信息-说明
        skuid = re.search("skuid:\s*(\d+?),", response.text).group(1)
        venderId = re.search("venderId:\s*(\d+?),", response.text).group(1)
        cat = re.search("cat:\s*\[(.+?)\]", response.text).group(1)
        instruction = requests.get(self.instru_uri.format(skuid, venderId, cat)).text
        document["售后信息"]["说明"].extend(re.findall('"showName":\s*"(.*?)"', instruction))

        # 售后信息-更多说明
        for instru in response.xpath('//*[@class="more-con"]//li'):
            document["售后信息"]["更多说明"].append(from_xpath(instru, './/text()', type=xt.string_join))

        # 详情信息-商品详情
        for goodsInfo in response.xpath('//*[@class="p-parameter"]//li'):
            key, value = re.search('(.*?)[:：](.*)', from_xpath(goodsInfo, './/text()', type=xt.string_join),
                                   re.S).groups()
            if all((key, value)):
                document["详情信息"]["商品详情"][key.strip()] = value.strip()

    def validCaptcha(self, response):  # 验证码识别
        storeId = response.meta["storeId"]
        tryCount = response.meta["tryCount"]
        document = response.meta["document"]
        cookies = dict()
        for header, values in response.headers.items():
            if header == b"Set-Cookie":
                cookie = "".join([cookie.decode() for cookie in values])
                cookies['JSESSIONID'] = re.search('JSESSIONID=(.*?);', cookie).group(1)
                _jshop_vd_ = re.search('_jshop_vd_=(.*?);', cookie)
                if _jshop_vd_:  # 国内验证码
                    cookies['_jshop_vd_'] = _jshop_vd_.group(1)
                _jshop_vd_hk_ = re.search('_jshop_vd_hk_=(.*?);', cookie)
                if _jshop_vd_hk_:  # 跨境电商验证码
                    cookies['_jshop_vd_hk_'] = _jshop_vd_hk_.group(1)
                break
        yield FormRequest(
            self.license_uri.format(storeId),
            formdata={
                "verifyCode": captcha(response.body)
            },
            meta={
                "storeId": storeId,
                "tryCount": tryCount,
                "document": document
            },
            cookies=cookies,
            callback=self.parseLicense
        )

    def parseLicense(self, response):
        storeId = response.meta["storeId"]
        tryCount = response.meta["tryCount"]
        document = response.meta["document"]
        if "验证码" in response.text:
            self.log("验证码失败了...重试: {} storeId: {}".format(tryCount, storeId), logging.WARNING)
            if "京东商城网店经营者资质信息" in response.text:
                yield self.captchaRequest(storeId, tryCount + 1, document=document)
            elif "京东国际网店经营者资质信息" in response.text:  # 转跨境电商
                self.log("转跨境电商验证码: {}".format(storeId))
                yield self.captchaRequest(storeId, tryCount + 1, document=document, uri=self.cross_captcha_uri)
            else:
                self.log("证书页面改版了, 当前url: {}".format(response.url), logging.ERROR)
        elif "京东商城网店经营者营业执照信息" in response.text \
                or "京东国际网店经营者资质信息" in response.text:
            for picUri in response.xpath('//*[@class="qualification-img"]/@src').extract():
                picUri = response.urljoin(picUri)
                document["企业资质"]["证件截图"].append(img2base64(picUri))
            for li in response.xpath('//*[@class="jScore"]//li'):
                text = from_xpath(li, './/text()', type=xt.string_join)
                key, value = re.search('(.*?)[:：](.*)', text, re.S).groups()
                if all((key, value)):
                    document["企业资质"][strip_all(key)] = strip_all(value)

            # 商店评分
            appId = from_xpath(response, '//*[@id="pageInstance_appId"]/@value')
            if appId:
                text = requests.get(self.score_uri.format(appId)).text
                for key, value in re.findall('(用户评价|物流履约|售后服务|服务态度)[:：].*?(\d+\.\d+)', text, re.S):
                    document["店铺动态评分"][key] = value
        else:
            self.log("可能跳到其他页面或者改版了, 当前url: {}".format(response.url), logging.ERROR)


if __name__ == '__main__':
    target = ""
    MySpider.run(__file__, suffix=f"-s target={target} --loglevel INFO")
