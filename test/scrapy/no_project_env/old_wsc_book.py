# -*- coding:utf-8 -*-
import os
import re
import json
import execjs
import logging
from minitools.scrapy import miniSpider
from minitools.scrapy.pipelines import MONGODB_PIPELINE
from minitools import merge_dicts
from scrapy import Request, FormRequest

with open(os.path.join(os.path.dirname(__file__), 'zgcpwsw2.js'), encoding='utf-8') as f:
    js = f.read()
    anti_second = execjs.compile(js)

with open(os.path.join(os.path.dirname(__file__), 'zgcpwsw3.js'), encoding='utf-8') as f:
    js = f.read()
    anti_third = execjs.compile(js)


def refresh_post_data(page, vl5x, number, guid, param='案件类型:刑事案件'):
    post_data = {
        "Param": param,
        "Index": str(page),
        "Page": "10",
        "Order": "裁判日期",
        "Direction": "asc",
        "vl5x": str(vl5x),
        "number": 'oldw',
        "guid": str(guid),
    }
    return post_data


class MySpider(miniSpider):
    name = "old_wsc_book"

    # for spider
    page = 1
    url = "http://oldwenshu.court.gov.cn/list/list/?sorttype=1"
    list_url = "http://oldwenshu.court.gov.cn/List/ListContent"
    detail_js_url = "http://oldwenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID="
    detail_doc_url = "http://wenshu.court.gov.cn/content/content?DocID="
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,und;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "oldwenshu.court.gov.cn",
        "Origin": "http://oldwenshu.court.gov.cn",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "",
    }

    # for scrapy
    mongodb = None
    mongodb_client = None
    custom_settings = merge_dicts(
        MONGODB_PIPELINE,
        {
            "CONCURRENT_REQUESTS": 1,
            "DOWNLOAD_DELAY": 4,
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
            "mongodb_db": name,
            "mongodb_coll": name,
            "mongodb_config": {},
        }
    )

    def start_requests(self):
        target = self.crawler.settings.get("target")
        if target:
            self.log(f"Get Target: {target}")
            self.keyword = target if ":" in target else f"全文检索:{target}"
            yield self.new_vl5x()
        else:
            raise RuntimeError("Please input search target, you may need `-s target=something`")

    def new_vl5x(self):
        return Request(self.url, dont_filter=True)

    def parse(self, response):
        vjkl5 = re.search("vjkl5=(.*?);", str(response.headers)).group(1)
        vl5x, guid, number = anti_second.call('anti_second', vjkl5)
        formdata = refresh_post_data(self.page, vl5x, number, guid, self.keyword)
        self.log("current page: {}".format(self.page), level=logging.INFO)
        headers = self.headers.copy()
        headers['Cookie'] = f"vjkl5={vjkl5};"
        yield FormRequest(self.list_url, formdata=formdata, headers=headers, callback=self.parse_list,
                          meta={'dont_redirect': True})

    def parse_list(self, response):
        try:
            data = json.loads(json.loads(response.text))
            runeval = data[0]["RunEval"]
            count = data[0].get("Count")
            if not count:
                self.logger.info(f"无符合条件的数据:{count}, json data is:{data}")
                return
            self.logger.info(f"共找到{count}个结果")
        except:
            self.logger.info("parse解析失败")
            yield self.new_vl5x()
            return
        new = 0
        for doc in data[1:]:
            try:
                docId = doc['文书ID']
            except KeyError:
                continue
            DocID = anti_third.call('anti_third', runeval, docId)
            url = self.detail_doc_url + DocID
            json_url = self.detail_js_url + DocID
            if self.mongodb_client.count({"URL": url}):
                continue
            new += 1
            yield {"url": url, "json_url": json_url}
        self.log(f"new item: {new}", level=logging.INFO)
        if self.page < 20:  # force turn page until 20.
            self.page += 1
            yield self.new_vl5x()


if __name__ == '__main__':
    MySpider.run(__file__, suffix="-s target=法院名称:铜仁市万山区人民法院")
