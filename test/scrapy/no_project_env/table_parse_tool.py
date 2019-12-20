from minitools.scrapy import miniSpider
from minitools import tableParser


class MySpider(miniSpider):
    # start_urls = ["http://hbj.nanjing.gov.cn/zwgk/xzzf/201912/t20191216_1740273.html"]
    start_urls = ["http://www.nxgy.gov.cn/zwgk/zfxxgkml/rsxx/rdcwhrsrm/201911/t20191101_1835995.html"]

    def parse(self, response):
        # a = tableParser.create(response, '//*[contains(text(), "行政处罚决定书文号")]/ancestor::table[1]').to_dict()
        a = tableParser.create(response, '//*[@class="zm-table3"]').to_dict_by_one()
        from pprint import pprint
        pprint(a)


if __name__ == '__main__':
    MySpider.run(__file__)
