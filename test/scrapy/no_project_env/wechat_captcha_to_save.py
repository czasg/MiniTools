# -*- coding: utf-8 -*-
import re
import json
import datetime
import functools
from scrapy import Request, FormRequest
from minitools.scrapy import miniSpider

PROXY_WITHOUT_PROTOCOL = re.compile("(?:https?://)*(.*)").search
VERIFY_URL = "http://www.baidu.com/"


def str_timestamp(len): return str(int(datetime.datetime.timestamp(datetime.datetime.now()) * (10 ** (len - 10))))


def get_code_from_captcha(content, model=None, is_b64=False, url=None):
    """Unable to upload to gits"""


def save_right_captcha(spider, body, label, right=True):
    """Unable to upload to gits"""


class MySpider(miniSpider):
    start_urls = [
        "https://weixin.sogou.com/antispider/?from=%2Fweixin%3Ftype%3D2%26query%3DLtcyw-2009%26ie%3Dutf8%26s_from%3Dinput%26_sug_%3Dn%26_sug_type_%3D1%26w%3D01015002%26oq%3D%26ri%3D48%26sourceid%3Dsugg%26sut%3D0%26sst0%3D1576220394389%26lkt%3D0%2C0%2C0%26p%3D40040108"
    ]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 0.3,
    }
    img_url = functools.partial(lambda x: "https://weixin.sogou.com/antispider/util/seccode.php?tc=" + str_timestamp(x))
    thank_url = "https://weixin.sogou.com/antispider/thank.php"

    def start_requests(self):
        yield self.new_request()

    def new_request(self):
        return Request(self.start_urls[0], dont_filter=True)

    def parse(self, response):
        if 'antispider' in response.url:
            self.r = re.search("from=([^&]+)", response.url).group(1)
            yield Request(self.img_url(13), self.process_img, dont_filter=True)

    def process_img(self, response):
        code = get_code_from_captcha(response.body)
        data = {"r": self.r, "v": "5", "c": code}
        yield FormRequest(self.thank_url, formdata=data, callback=self.process_result,
                          meta={'captcha_body': response.body, 'label': code}, dont_filter=True)

    def process_result(self, response):
        info = json.loads(response.text)
        if info["code"] == 0:
            self.log("Authentication is successful!")
            save_right_captcha(self, response.meta['captcha_body'], response.meta['label'])
            yield self.new_request()
        else:
            self.log("Retry Again!")
            yield self.new_request()


if __name__ == '__main__':
    MySpider.run(__file__)
