# -*- coding: utf-8 -*-
import os
import queue
import weakref
import chardet
import atexit
import inspect
import itertools
import threading

from requests import session
from parsel import Selector
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, Future

__all__ = ('Response', 'Request', 'Spider')

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False
default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}


def _python_exit():
    global _shutdown
    _shutdown = True
    items = iter(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()


atexit.register(_python_exit)


class Response(Selector):
    """
    应该仅仅只是用来存放结果的一个对象，再附带一些对处理结果可能有用的函数
    """
    __slots__ = ['text', 'namespaces', 'type', '_expr', 'root',
                 '_parser', '_csstranslator', '_tostring_method', 'url']

    def __init__(self, text=None, type=None, namespaces=None, root=None,
                 base_url=None, _expr=None, url=None):
        self.url = url
        self.text = text
        super(Response, self).__init__(text, type, namespaces, root, base_url, _expr)

    def urljoin(self, url):
        return urljoin(self.url, url)


class Request:
    """
    应该仅仅只是用来存放请求数据的一个对象，再附带一些对发请请求可能有用的函数
    """

    def __init__(self, spider, url=None, method='GET', data=None, headers=None, params=None, json=None,
                 callback=None, session=None, future=None):
        self.spider = spider
        self.url = url or spider.url
        self.method = method
        self.data = data
        self.headers = default_headers.update(headers or {})
        self.params = params or {}
        self.json = json or {}
        self.callback = callback
        self.session = session
        self.future = future

    def set_session(self, session):
        self.session = session

    def set_future(self, future):
        self.future = future


def _worker(executor_reference, work_queue):
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                del work_item
                continue
            executor = executor_reference()
            if _shutdown or executor is None or executor._shutdown:
                if executor is not None:
                    executor._shutdown = True
                work_queue.put(None)
                return
            del executor
    except:
        pass


def _downloader(request):
    request.set_session(request.spider.session)
    content = request.session.request(request.method, request.url,
                                      data=request.data, headers=request.headers,
                                      params=request.params, json=request.json).content
    text = content.decode(request.spider.coding or chardet.detect(content)['encoding'])
    generator_or_result = (request.callback or request.spider.parse)(Response(text=text, url=request.url))
    return generator_or_result


class _WorkItem:
    def __init__(self, future, request):
        self.future = future
        self.request = request

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            result = self.request.spider._downloader(self.request)
        except BaseException as exc:
            self.future.set_exception(exc)
            self = None
        else:
            self.future.set_result(result)


class Spider:
    """
    这里应该是一个开发人员启动器
    """
    url = ''

    coding = "utf-8"
    queue = queue.Queue()
    session = session()
    _max_thread = (os.cpu_count() or 1) * 5
    _counter = itertools.count().__next__

    def __init__(self):
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(self._max_thread)
        self._downloader = _downloader

    def start_requests(self):
        yield Request(self)

    @classmethod
    def run(cls):
        with cls() as spider:
            for request in spider.start_requests():
                with spider._shutdown_lock:
                    if spider._shutdown:
                        raise RuntimeError("Spider has shutdown, cannot schedule new task")
                    if _shutdown:
                        raise RuntimeError("interpreter has shutdown, cannot schedule new task")
                    spider.add_request(request)
                    spider._run()

    def add_request(self, request):
        def _callback(future, add_request=self.add_request):
            generator_or_result = future.result()
            if inspect.isgenerator(generator_or_result):
                for request in generator_or_result:
                    add_request(request)

        f = Future()
        request.set_future(f)
        f.add_done_callback(_callback)
        self.queue.put(_WorkItem(f, request))

    def _run(self):
        def _callback(_, queue=self.queue):
            queue.put(None)

        thread_count = len(self._threads)
        if thread_count < self._max_thread:
            thread_name = f"minispider-{self._counter()}_{thread_count}"
            t = threading.Thread(name=thread_name, target=_worker, args=(
                weakref.ref(self, _callback),
                self.queue
            ))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self.queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self.queue.put(None)
        if wait:
            for t in self._threads:
                t.join()

    def parse(self, response):
        """No thing to do"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
        return False


if __name__ == '__main__':
    class S(Spider):
        url = "http://192.168.0.110:3031/"

        def parse(self, response): ...
        # print(response.text)


    S.run()
