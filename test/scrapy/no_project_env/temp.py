from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    """todo, 为什么会打印翻页的日志，实际上应该是啥也没干嘛"""


if __name__ == '__main__':
    MySpider.run(__file__)
