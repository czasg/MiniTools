import logging
from collections import defaultdict
from minitools import get_proxy, check_proxy
from scrapy.downloadermiddlewares.retry import RetryMiddleware

__all__ = 'PROXY_POOL_RETRY_MIDDLEWARE',

# when one Request fail and retry, it will random.choice one proxy-ip into a proxy-ip-pool
# each retries, every Retry-Request will choose latest proxy in proxy-ip-pool
PROXY_POOL_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyPoolRetryMiddleware': 550,
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


class ProxyPoolRetryMiddleware(BaseProxyRetryMiddleware):

    def __init__(self, settings, get_proxy):
        super(ProxyPoolRetryMiddleware, self).__init__(settings, get_proxy)
        self.error_stats = defaultdict(int)

    def process_request(self, request, spider):
        if self.proxies:
            spider.log("use latest proxies...")  # log level: debug
            request.meta["proxy"] = self.proxies[-1]
        else:
            mini_proxy = getattr(spider, "mini_proxy")  # log level: debug
            if mini_proxy:
                spider.log("use mini_proxy...")
                request.meta["proxy"] = mini_proxy

    def _retry(self, request, reason, spider):
        req = super()._retry(request, reason, spider)
        stats = spider.crawler.stats
        if req:
            def _suitable_proxy_request(request):
                if not self.proxies:
                    _push_proxy()
                try:
                    if 'proxy' in request.meta:
                        index = self.proxies.index(request.meta['proxy'])
                        proxy = self.proxies[index + 1]
                        pre_error_proxy = self.proxies[index]
                        self.error_stats[pre_error_proxy] += 1
                        if self.error_stats[pre_error_proxy] == 3:
                            self.proxies.remove(pre_error_proxy)
                    else:
                        proxy = self.proxies[-1]
                    spider.log(f"new {proxy} from proxy-ip-pool for {request.url}", level=logging.INFO)
                    return request_replace_proxy_meta(request, proxy)
                except ValueError:  # not find the proxy.
                    return request_replace_proxy_meta(request, self.proxies[0])
                except IndexError:  # ProxyAgent pool is exhaustion. push new one in it.
                    _push_proxy()
                    return _suitable_proxy_request(request)

            def _push_proxy():
                stats.inc_value('mini/proxy/count')
                self.proxies.append(check_proxy(self.get_proxy()))
                spider.log(f"add new proxy-ip, current pool: {self.proxies}", level=logging.INFO)

            return _suitable_proxy_request(req)


def request_replace_proxy_meta(request, proxy):
    meta = request.meta
    meta['proxy'] = proxy
    return request.replace(meta=meta, priority=1, dont_filter=True)
