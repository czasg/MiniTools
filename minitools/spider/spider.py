import queue
from requests import session
from parsel import Selector
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

__all__ = ('Response', 'Request', 'Spider')

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
running = 0


class Response(Selector):
    __slots__ = ['text', 'namespaces', 'type', '_expr', 'root',
                 '_parser', '_csstranslator', '_tostring_method', 'base_url']

    def __init__(self, text=None, type=None, namespaces=None, root=None,
                 base_url=None, _expr=None):
        self.base_url = base_url
        self.text = text
        super(Response, self).__init__(text, type, namespaces, root, base_url, _expr)

    def urljoin(self, url):
        return urljoin(self.base_url, url)


class Request:
    def __init__(self, spider, url=None, method='GET', data=None, headers=None, params=None, json=None,
                 callback=None, session=None):
        self.spider = spider
        self.url = url or spider.url
        self.method = method
        self.data = data
        self.headers = headers or default_headers
        self.params = params or {}
        self.json = json or {}
        self.callback = callback
        self.session = session

    def _run(self):
        global running
        running += 1
        self.set_session(self.spider.session)
        text = self.session.request(self.method, self.url,
                                    data=self.data, headers=self.headers,
                                    params=self.params, json=self.json).text
        self.done(text)
        running -= 1

    def set_session(self, session):
        self.session = session

    def done(self, text):
        (self.callback or self.spider.parse)(Response(text=text, base_url=self.url))


class Spider:
    url = ''

    queue = queue.Queue()
    session = session()
    executor = ThreadPoolExecutor(10)

    def start_requests(self):
        yield Request(self)

    @classmethod
    def run(cls):
        spider = cls()
        for request in spider.start_requests():
            spider.add_request(request)
        spider._run()

    def _run(self):
        while (self.queue.qsize() or running):
            try:
                request = self.queue.get(block=False)
                self.executor.submit(request._run)
            except queue.Empty:
                continue

    def add_request(self, request):
        self.queue.put(request)

    def parse(self, response):
        """No thing to do"""
