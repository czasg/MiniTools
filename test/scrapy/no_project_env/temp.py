from minitools.scrapy import miniSpider
from scrapy import Request
from minitools.scrapy.squeues import test_path


class MySpider(miniSpider):
    start_urls = ["http://www.baidu.com"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 1,
        # "SCHEDULER_DISK_QUEUE": test_path,
    }

    def parse(self, response): ...

    # self.log("Hello world")
    # import time
    # for i in range(100):
    #     request = response.request
    #     request.dont_filter = True
    #     request.callback = self.parse1
    #     # request.priority = i
    #     yield request

    def parse1(self, response):
        # self.crawler.engine.close_spider(self, 'just/for/text')
        print(response.request.priority, 'from parse1')


if __name__ == '__main__':
    import os

    MySpider.run(__file__, suffix=f"-s JOBDIR={os.path.dirname(__file__)}")

    # import os
    # import struct
    #
    # SIZE_FORMAT = ">L"
    # SIZE_SIZE = struct.calcsize(SIZE_FORMAT)
    # with open("cza.txt", 'rb') as f:
    #     f.seek(-SIZE_SIZE, os.SEEK_END)
    #     size, = struct.unpack(SIZE_FORMAT, f.read())
    #     f.seek(-size-SIZE_SIZE, os.SEEK_END)
    #     data = f.read(size)
    #     print(data)

    # for string in [
    #     b'aaaaaaaaaaaaaaaaaaaaa',
    #     b'bbbbbbbbbbbbbbbbbbbbb',
    #     b'ccccccccccccccccccccc',
    #     b'ddddddddddddddddddddd',
    #     b'fffffffffffffffffffff',
    #     b'ggggggggggggggggggggg',
    # ]:
    #     f.write(string)
    #     ssize = struct.pack(SIZE_FORMAT, len(string))
    #     f.write(ssize)
