from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.baidu.com/"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
    }

    def parse(self, response):
        count = 0
        for i in range(2):
            count += 1
            yield response.request.replace(dont_filter=True, meta={'count': count, 'flag': 1}, callback=self.parse1)

    def parse1(self, response):
        print(response.meta)
        count = 0
        for i in range(3):
            count += 1
            yield response.request.replace(dont_filter=True, meta={'count': count, 'flag': 2}, callback=self.parse2)

    def parse2(self, response):
        # self.crawler.engine.close_spider(self, 'just/for/text')
        print(response.meta)


if __name__ == '__main__':
    import os

    MySpider.run(__file__, suffix=f"-s JOBDIR={os.path.dirname(__file__)}")

    # import struct
    # import os
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
