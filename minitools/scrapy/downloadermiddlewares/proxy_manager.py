import logging

from minitools import get_proxy

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import NotConfigured

__all__ = 'PROXY_RETRY_MIDDLEWARE', 'PROXY_POOL_RETRY_MIDDLEWARE', 'PROXY_MIDDLEWARE',

PROXY_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyRetryMiddleware': 550,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyMiddleware': 50,

    }
}
PROXY_POOL_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyPoolRetryMiddleware': 550,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyMiddleware': 50,

    }
}
PROXY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyMiddleware': 50,
    }
}


class BaseProxyRetryMiddleware(RetryMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        get_proxy_func = crawler.spider.get_proxy if hasattr(crawler.spider, 'get_proxy') else get_proxy
        return cls(crawler.settings, get_proxy_func)

    def __init__(self, settings, get_proxy):
        super(BaseProxyRetryMiddleware, self).__init__(settings)
        self.get_proxy = get_proxy
        self.proxies = []


class ProxyRetryMiddleware(BaseProxyRetryMiddleware):

    def _retry(self, request, reason, spider):
        req = super()._retry(request, reason, spider)
        stats = spider.crawler.stats
        if req:
            proxy = self.get_proxy()  # todo, 逻辑果然不行. scrapy的调度会把所有已入队的线处理掉, 后续在推入的是另外算的吗?
            spider.log(f"请求异常, 获取到新代理proxy: {proxy}, 进入重试", level=logging.INFO)
            if proxy:
                stats.inc_value('mini/proxy/count')
                proxy = check_proxy(proxy)
                spider.log(f"请求异常, 获取到新代理proxy: {proxy}, 进入重试", level=logging.INFO)
                return req.replace(meta={'proxy': proxy})
            return req


class ProxyPoolRetryMiddleware(BaseProxyRetryMiddleware):

    def _retry(self, request, reason, spider):  # todo, 同上
        req = super()._retry(request, reason, spider)
        stats = spider.crawler.stats
        if req:
            def _suitable_proxy_request(request):
                if not self.proxies:
                    _push_proxy()
                try:
                    if 'proxy' in request.meta:
                        proxy = self.proxies[self.proxies.index(request.meta['proxy']) + 1]
                    else:
                        proxy = self.proxies[0]
                    return request.replace(meta={'proxy': proxy})
                except ValueError:  # not find the proxy
                    return request.replace(meta={'proxy': self.proxies[0]})
                except IndexError:  # ProxyAgent poll is exhaustion. push new one in
                    _push_proxy()
                    return _suitable_proxy_request(request)

            def _push_proxy():
                stats.inc_value('mini/proxy/count')
                spider.log(f"请求异常, 添加新代理proxy重试, 当前代理池: {self.proxies}", level=logging.INFO)
                self.proxies.append(check_proxy(self.get_proxy()))

            return _suitable_proxy_request(req)


class ProxyMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler
        self.mini_proxy = crawler.spider.mini_proxy if hasattr(crawler.spider, 'mini_proxy') else None

    def process_request(self, request, spider):
        if self.mini_proxy and 'proxy' not in request.meta:  # ignore if proxy is already set
            request.meta['proxy'] = check_proxy(self.mini_proxy)

    def process_response(self, request, response, spider):
        retry_times = request.meta.get('retry_times', 0)
        proxy = request.meta.get('proxy', None)
        if retry_times and proxy:
            self.mini_proxy = proxy  # save the good quality proxy


def check_proxy(proxy):
    return proxy if proxy.startswith('http') else f"http://{proxy}"
