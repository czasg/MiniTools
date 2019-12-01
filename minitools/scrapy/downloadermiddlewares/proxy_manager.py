import logging

from minitools import get_proxy

from scrapy.downloadermiddlewares.retry import RetryMiddleware

__all__ = 'PROXY_RETRY_MIDDLEWARE',

PROXY_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyRetryMiddleware': 550
    }
}


class ProxyRetryMiddleware(RetryMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        get_proxy_func = crawler.spider.get_proxy if hasattr(crawler.spider, 'get_proxy') else get_proxy
        return cls(crawler.settings, get_proxy_func)

    def __init__(self, settings, get_proxy):
        super(ProxyRetryMiddleware, self).__init__(settings)
        self.get_proxy = get_proxy

    def _retry(self, request, reason, spider):
        req = super()._retry(request, reason, spider)
        if req:
            proxy = self.get_proxy()
            spider.log(f"请求异常, 获取到新代理proxy: {proxy}, 进入重试", level=logging.INFO)
            return req.replace(meta={'proxy': f"http://{proxy}"}) if proxy else req
