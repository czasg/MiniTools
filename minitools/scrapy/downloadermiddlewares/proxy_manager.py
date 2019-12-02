import logging

from minitools import get_proxy, merge_dict

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import NotConfigured

__all__ = ('PROXY_RETRY_MIDDLEWARE', 'PROXY_POOL_RETRY_MIDDLEWARE', 'FIXED_PROXY_MIDDLEWARE',
           'FIXED_PROXY_RETRY_MIDDLEWARE', 'FIXED_PROXY_POOL_RETRY_MIDDLEWARE')

# when one Request fail and retry, it will random.choice one proxy-ip for the new Request
# each retries, the proxy-ip maybe different for Request
PROXY_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyRetryMiddleware': 550,
    }
}

# when one Request fail and retry, it will random.choice one proxy-ip into a proxy-ip-pool
# each retries, every Retry-Request will choose first proxy in proxy-ip-pool
# and the second retry in same Request, it will choose next proxy in proxy-ip-pool
PROXY_POOL_RETRY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.ProxyPoolRetryMiddleware': 550,
    }
}

# This proxy from ProxyMiddleware will just works once for a new Request which hasn't `proxy`,
# if you need change it, you should use ProxyRetryMiddleware/ProxyPoolRetryMiddleware.
FIXED_PROXY_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
        'minitools.scrapy.downloadermiddlewares.proxy_manager.FixedProxyMiddleware': 50,
    }
}

FIXED_PROXY_RETRY_MIDDLEWARE = merge_dict(FIXED_PROXY_MIDDLEWARE, PROXY_RETRY_MIDDLEWARE)
FIXED_PROXY_POOL_RETRY_MIDDLEWARE = merge_dict(FIXED_PROXY_MIDDLEWARE, PROXY_POOL_RETRY_MIDDLEWARE)


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
            proxy = self.get_proxy()
            if proxy:
                stats.inc_value('mini/proxy/count')
                proxy = check_proxy(proxy)
                spider.log(f"get one new proxy: {proxy} for {request.url}", level=logging.INFO)
                return request_replace_proxy_meta(req, proxy)
            return req


class ProxyPoolRetryMiddleware(BaseProxyRetryMiddleware):

    def _retry(self, request, reason, spider):
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
                    spider.log(f"new {proxy} from proxy-ip-pool for {request.url}", level=logging.INFO)
                    return request_replace_proxy_meta(request, proxy)
                except ValueError:  # not find the proxy.
                    return request_replace_proxy_meta(request, self.proxies[0])
                except IndexError:  # ProxyAgent poll is exhaustion. push new one in.
                    _push_proxy()
                    return _suitable_proxy_request(request)

            def _push_proxy():
                stats.inc_value('mini/proxy/count')
                self.proxies.append(check_proxy(self.get_proxy()))
                spider.log(f"add new proxy-ip, current pool: {self.proxies}", level=logging.INFO)

            return _suitable_proxy_request(req)


class FixedProxyMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return cls(crawler)

    def __init__(self, crawler):
        if not hasattr(crawler.spider, 'mini_proxy'):
            raise AttributeError("ProxyMiddleware need a property of `mini_proxy`")
        self.mini_proxy_log = True

    def process_request(self, request, spider):
        mini_proxy = spider.mini_proxy
        if mini_proxy and self.mini_proxy_log:
            self.mini_proxy = mini_proxy
            self.mini_proxy_log = False
            spider.log(f"using proxy:ip --- {self.mini_proxy}", level=logging.INFO)
        if mini_proxy and 'proxy' not in request.meta:  # ignore if proxy is already set
            request.meta['proxy'] = check_proxy(self.mini_proxy)

    def process_response(self, request, response, spider):
        retry_times = request.meta.get('retry_times', 0)
        proxy = request.meta.get('proxy', None)
        if retry_times and proxy:
            self.mini_proxy = proxy  # save the good quality proxy.
        return response


def check_proxy(proxy):
    return proxy if proxy.startswith('http') else f"http://{proxy}"


def request_replace_proxy_meta(request, proxy):
    meta = request.meta
    meta['proxy'] = proxy
    return request.replace(meta=meta, dont_filter=True)
