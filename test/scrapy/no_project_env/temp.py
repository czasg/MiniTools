from minitools.scrapy import miniSpider
from minitools.scrapy import refresh_response


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        print(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)

    # import subprocess
    #
    # subprocess.call(f"scrapy runspider {__file__}")

    # todo, scrapy crawl -o cza.json.  can i use this way to save data without pipeline?
    # todo, 付费代理还需要加入统计机制，也就是统计删除的意思
