from twisted.internet import task
from scrapy import signals

__all__ = 'close_spider_without_increment',

close_spider_without_increment = {
    'EXTENSIONS': {
        'minitools.scrapy.extensions.closespiderwithoutincrement.CloseSpiderWithoutIncrement': 0
    }
}


class CloseSpiderWithoutIncrement:

    def __init__(self, crawler):
        self.crawler = crawler
        self.stats = crawler.stats
        self.interval = crawler.settings.getint('CLOSESPIDER_CHECKINTERVAL', 33)
        self.cache = None
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.loop_check, spider)
        self.task.start(self.interval)

    def loop_check(self, spider):
        self.increment_count = self.stats.get_value('increment/count', 0)
        if self.increment_count == self.cache:
            self.crawler.engine.close_spider(spider, 'close/spider/without/increment')
        else:
            self.cache = self.increment_count

    def spider_closed(self, spider):
        if self.task and self.task.running:
            self.task.stop()
