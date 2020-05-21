"""
京东爬虫流程
使用搜索词访问搜索页面，需要到此页面拿cookie
携带此cookie直接访问ajax的搜索接口，拿到商品数据
此处均无反爬...

从商品页面拿到店铺id，直接用id访问证书页面
此时必定出现验证码
验证码的机制是，每访问一个验证码，就会返回一set-cookie，这个cookie是一次性的，不能共享
所以该图片返回的cookie不能merge，需要单独取出来

验证码：
直接访问验证码，拿到图片和cookie，取出cookie，验证码识别，然后带着一起访问证书页面即可
"""

import time
import base64
import logging
import random
import requests
import datetime

from scrapyProj.basespiders.shortcut import LLBaseSpider
from scrapyProj.tools import *
from scrapyProj.tools.captcha import get_code_from_captcha
from scrapyProj.candy.商城类.data import Store, Good, Image
from scrapyProj.tools.proxy import get_wan_proxy


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
    name = "京东商城"
    dbName = "商城类"
    collName = "京东商城"
    cat = "零碎任务"
    website_name = "京东商城"
    website_url = "https://www.jd.com/"

    url = "https://search.jd.com/Search?keyword={}&enc=utf-8&pvid=adc505dac9d2429a95b6da44b7575ead"  # 搜索接口
    captcha_uri = lambda *args: "https://mall.jd.com/sys/vc/createVerifyCode.html?random={}".format(
        random.random())  # 国内电商验证码接口
    cross_captcha_uri = lambda *args: "https://mall.jd.hk/sys/vc/createVerifyCode.html?random={}".format(
        random.random())  # 跨境电商验证码接口
    license_uri = "https://mall.jd.com/showLicence-{}.html"  # 证书接口
    search_uri = "https://search.jd.com/s_new.php?keyword={}&enc=utf-8&page=1"  # ajax搜索接口
    instru_uri = "https://c0.3.cn/stock?skuId={}&venderId={}&callback=jQuery9683234&cat={}&area=17_1381_50718_0"  # 说明链接
    comment_uri = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}&callback=jQuery1295277"
    score_uri = "https://mall.jd.com/view/getJshopHeader.html?callback=jQuery4335455&appId={}"
    searchKey = "数博科技"
    tempGoodsSet = set()
    tempStoreSet = set()
    spiderproxy = None

    custom_settings = csp.ll_extra_settings(
        {
            "DOWNLOAD_DELAY": 1.5,
        },
        csp.get_proxy_setting(mode=csp.SPIDER_PROXY),
    )

    def raiseAndCatchError(self):
        info = "此次查询已记录为异常：`{}` 查询结果为空，直接返回".format(self.searchKey)
        self.log(info, logging.ERROR)
        self.emptySearchColl.insert_one({"type": self.collName, "key": self.searchKey})
        self.crawler.engine.close_spider(self, info)

    def start_requests(self):
        self.searchKey = self.crawler.settings.get("target")
        self.allowGoods = False
        self.searchByUrl = False
        if not self.searchKey:
            raise Exception("未指定搜索关键词")
        self.log("获取到店铺名称: {}".format(self.searchKey))

        if self.searchKey.startswith('goods:'):
            self.allowGoods = True
            self.searchKey = self.searchKey.replace('goods:', '')
        elif self.searchKey.startswith('url:'):
            self.searchByUrl = True
            self.searchKey = self.searchKey.replace('url:', '')

        self.goodsColl = self.client[self.dbName][self.collName + "(商品信息)"]
        self.storesColl = self.client[self.dbName][self.collName + "(店铺信息)"]
        self.emptySearchColl = self.client[self.dbName]["空查询"]
        self.errorStoreColl = self.client[self.dbName]["异常店铺"]

        if self.emptySearchColl.count({"type": self.collName, "key": self.searchKey}):
            return self.log("查询结果为空，爬虫结束".format(self.searchKey), logging.ERROR)
        if self.allowGoods:  # 商品
            self.spiderproxy = get_wan_proxy(p=0.4)
        elif self.searchByUrl:  # 店铺链接
            if self.storesColl.count({"店铺链接": self.searchKey}):
                return self.log('该条记录已存在', logging.INFO)
            storeId = rea.search('index-(\d+)', self.searchKey).group(1)
            if storeId and self.storesColl.count({"店铺ID": storeId}):
                return self.log('该条记录已存在', logging.INFO)
            self.spiderproxy = get_wan_proxy(p=0.7)
        else:  # 店铺
            if self.storesColl.count({"店铺名称": self.searchKey}):
                return self.log('该条记录已存在', logging.INFO)
            self.spiderproxy = get_wan_proxy(p=0.2)
        yield Request(self.url.format(self.searchKey), callback=self.patchCookies)

    def patchCookies(self, response):  # 需要先跳转搜索页拿cookies
        if self.searchByUrl:
            yield Request(self.searchKey, self.storePageParse)
        else:
            search_uri = self.search_uri.format(self.searchKey)
            yield Request(search_uri)

    def captchaRequest(self, storeId, tryCount=0, document=None, uri=None):
        """
        :param storeId: 店铺id
        :param tryCount: 验证码重试次数
        :return:
        """
        if tryCount > 5: return
        return Request(uri or self.captcha_uri(), self.validCaptcha, priority=1, meta={
            "storeId": storeId,
            "dont_merge_cookies": True,
            "tryCount": tryCount,
            "document": document or {}
        }, dont_filter=True)

    def parse(self, response):
        if "抱歉，没有找到与" in response.text:
            return self.raiseAndCatchError()

        goodsNew = storesNew = storesNotMatch = 0
        stores = response.xpath('//*[@id="J_goodsList"]//li[@class="gl-item"]')
        for store in stores:
            storeUrl = xpath(store, './/*[@class="p-shop"]//a/@href')
            if not storeUrl:
                continue
            storeUrl = response.urljoin(storeUrl)
            storeId = rea.search('index-(\d+)\.html', storeUrl).group(1)
            if not storeId:
                continue
            goodsUrl = xpath(store, './/*[@class="p-img"]/a/@href')
            if not goodsUrl:
                continue
            goodsUrl = response.urljoin(goodsUrl)
            title = xpath(store, './/*[@class="p-img"]/a/@title')
            content = wenben(store, './/*[@class="p-name p-name-type-2"]')
            storeName = xpath(store, './/*[@class="p-shop"]//a/text()')

            # if storeName != self.searchKey:  # 展示店铺与搜索关键词不一致，则认为此商店已倒闭或者改名了
            #     storesNotMatch += 1
            #     continue

            if self.allowGoods and goodsUrl not in self.tempGoodsSet:
                if goodsNew > 9: continue
                self.tempGoodsSet.add(goodsUrl)
                if not self.goodsColl.count({"商品网址": goodsUrl, "商品名称": title}):
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
                        },
                        "累计评价": "",
                        "商品销量": "",
                        "价格信息": dict()
                    }
                    for img in store.xpath('.//*[@class="ps-main" or @class="p-img"]//img'):  # 三种不同的页面结构
                        picUri = xpath(img, './@src|.//@data-lazy-img|.//@source-data-lazy-img')
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
                if storesNew > 2: continue
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
        self.log("商品信息: 共{}条其中{}条未爬".format(len(stores), goodsNew), logging.INFO)
        self.log("店铺信息: 共{}条其中{}条未爬".format(len(stores), storesNew), logging.INFO)
        # if goodsNew or storesNew:
        #     yield get_next_page_req(response, "page=%d")
        # if storesNotMatch == len(stores):
        #     return self.raiseAndCatchError()

    def storePageParse(self, response):
        if "error" in response.url or "您访问的页面" in response.text:
            return self.raiseAndCatchError()
        storeId = xpath(response, '//*[@id="shop_id"]/@value')
        if not storeId:
            return self.raiseAndCatchError()
        if self.storesColl.count({"店铺ID": storeId}):
            return self.log('该条记录已存在', logging.INFO)
        title = jxpath(response, '//title//text()')
        storeName = rea.search('(.*?)[-—]', title).group(1) or ''
        document = {
            "店铺名称": storeName,
            "店铺网址": response.url,
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

    def goodsPageParse(self, response):
        """
        商品页面解析
        :param response:
        :return:
        """
        document = response.meta["document"]

        # 商品下架
        if "该商品已下柜" in response.text:
            document["售后信息"]["说明"].append("该商品已下柜")

        # 售后信息-说明
        skuid = re.search("skuid:\s*(\d+?),", response.text).group(1)
        venderId = re.search("venderId:\s*(\d+?),", response.text).group(1)
        cat = re.search("cat:\s*\[(.+?)\]", response.text).group(1)
        instruction = requests.get(self.instru_uri.format(skuid, venderId, cat)).text
        document["售后信息"]["说明"].extend(re.findall('"showName":\s*"(.*?)"', instruction))
        document["价格信息"]["京东价"] = rea.search('"jdPrice":.*?"op":\s*"(.*?)"', instruction).group(1) or ""

        # 评论信息
        comment_text = requests.get(self.comment_uri.format(skuid)).text
        document["累计评价"] = rea.search('"CommentCount":\s*(\d+),', comment_text).group(1) or ""

        # 售后信息-更多说明
        for instru in response.xpath('//*[@class="more-con"]//li'):
            document["售后信息"]["更多说明"].append(jxpath(instru, './/text()'))

        # 详情信息-商品详情
        for goodsInfo in response.xpath('//*[@class="p-parameter"]//li'):
            key, value = rea.search('(.*?)[:：](.*)', jxpath(goodsInfo, './/text()'), re.S).groups()
            if all((key, value)):
                document["详情信息"]["商品详情"][key.strip()] = value.strip()

        # 详情信息-商品详情下面的宣传图片
        desc = rea.search("desc:\s*\'(//.+?)\'", response.text).group(1)
        if desc:
            try:
                description = requests.get(response.urljoin(desc)).json()
                for picUri in re.findall('(?:src|data-lazyload)="(.*?)"', description["content"]):
                    picUri = response.urljoin(picUri)
                    document["宣传图片"].append(Image({
                        "url": picUri,
                        "base64": img2base64(picUri)
                    }))
            except:
                self.log("商品页的宣传图片接口可能改版了", logging.WARNING)

        # 售后信息-售后保障
        guarantee = wenben(response, '//*[@id="guarantee"]')
        if guarantee:
            document["售后信息"]["更多说明"].append(guarantee)

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
                "verifyCode": get_code_from_captcha(response.body, model="jd_v1", log=False)
            },
            meta={
                "storeId": storeId,
                "tryCount": tryCount,
                "document": document
            },
            priority=2,
            cookies=cookies,
            callback=self.parseLicense
        )

    def parseLicense(self, response):
        """
        证书页面解析
        :param response:
        :return:
        """
        storeId = response.meta["storeId"]
        tryCount = response.meta["tryCount"]
        document = response.meta["document"]
        if "验证码" in response.text:
            self.log("验证码失败了...重试: {} storeId: {}".format(tryCount, storeId), logging.WARNING)
            if "京东商城网店经营者资质信息" in response.text:
                yield self.captchaRequest(storeId, tryCount + 1, document=document)
            elif "京东国际网店经营者资质信息" in response.text:  # 转跨境电商
                self.log("转跨境电商验证码: {}".format(storeId))
                yield self.captchaRequest(storeId, tryCount + 1, document=document, uri=self.cross_captcha_uri())
            else:
                self.log("证书页面改版了, 当前url: {}".format(response.url), logging.ERROR)
        elif "京东商城网店经营者营业执照信息" in response.text \
                or "京东国际网店经营者资质信息" in response.text:
            for picUri in response.xpath('//*[@class="qualification-img"]/@src').extract():
                picUri = response.urljoin(picUri)
                document["证件截图"].append(Image({
                    "url": picUri,
                    "base64": img2base64(picUri)
                }))
            for li in response.xpath('//*[@class="jScore"]//li'):
                text = jxpath(li, './/text()')
                key, value = rea.search('(.*?)[:：](.*)', text, re.S).groups()
                if all((key, value)):
                    document["企业资质"][strip_s(key)] = strip_s(value)

            # 商店评分
            appId = xpath(response, '//*[@id="pageInstance_appId"]/@value')
            if appId:
                text = requests.get(self.score_uri.format(appId)).text
                for key, value in re.findall('(用户评价|物流履约|售后服务|服务态度)[:：].*?(\d+\.\d+)', text, re.S):
                    document["店铺动态评分"][key] = value
            Store(document).save(self.storesColl)
        elif re.match("^https?://www.jd.com/?$", response.url):
            self.log("跳到首页了, 当前url: {}".format(response.url), logging.ERROR)
            self.errorStoreColl.insert_one({
                "type": self.collName,
                "key": self.searchKey,
                "msg": "跳转到了首页",
                "url": self.license_uri.format(storeId)
            })
            if not self.storesColl.count({"店铺ID": document["店铺ID"]}):
                Store(document).save(self.storesColl)
        else:
            self.log("可能跳到其他页面或者改版了, 当前url: {}".format(response.url), logging.ERROR)


if __name__ == '__main__':
    MySpider.run_download(suffix="-s target=url:https://mall.jd.com/index-829412.html --loglevel=DEBUG", fast=__file__)
