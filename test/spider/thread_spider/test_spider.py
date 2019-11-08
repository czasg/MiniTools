from minitools.spider.thread_spider import *


class MySpider(Spider):
    url = 'http://credit.wuhu.gov.cn/whweb/xygs/detailValue?tableName=T_MOULD_PUNISH&coulmnId=f13e789609fb459fa9c5cdaf64d49cbd'

    def start_requests(self):
        yield Request(self)

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    MySpider.run()

# todo, 下载或解析过程中，遇到报错就无法终止程序
