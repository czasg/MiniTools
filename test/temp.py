# -*- coding: utf8 -*-
import re
import os
import requests  # pip install requests
from io import BytesIO
from urllib.parse import urlparse
from itertools import count
from PIL import Image  # pip install Pillow
from parsel import Selector  # pip install parsel


def cur_path(pathname):
    return os.path.join(os.path.dirname(__file__), pathname)


def show_dynamic_ratio(cur_count, all_count, text='rate'):
    ratio = cur_count / all_count
    dynamic_ratio = int(ratio * 50)
    dynamic = '#' * dynamic_ratio + ' ' * (50 - dynamic_ratio)
    percentage = int(ratio * 100)
    print("\r[{}] {}: {}/{} {}%".format(dynamic, text, cur_count, all_count, percentage),
          end='', flush=True)


def save_image(body, output_name):
    byte_stream = BytesIO(body)
    im = Image.open(byte_stream)
    if im.mode == "P":
        im = im.convert('RGBA')
    if im.mode == "RGBA":
        im.load()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])
        im = background
    im.save('{}.jpg'.format(output_name), 'JPEG')


class Response(Selector):
    __slots__ = ['text', 'namespaces', 'type', '_expr', 'root',
                 '_parser', '_csstranslator', '_tostring_method', 'url']

    def __init__(self, text=None, type=None, namespaces=None, root=None,
                 base_url=None, _expr=None, url=None):
        self.url = url
        self.text = text
        super(Response, self).__init__(text, type, namespaces, root, base_url, _expr)


class RegexFilter:

    def __init__(self, title=None, time=None, src=None, domain=None or ['mmbiz.qpic.cn']):
        self.title_regex = title or re.compile('var msg_title = "(.*?)";')
        self.time_regex = time or re.compile(
            '"(\d{2,4}-\d{0,2}-\d{0,2})".*\n+.*document.getElementById\("publish_time"\)')
        self.domain_regex = re.compile(r'^(.*\.)?{}$'.format('|'.join(domain)))
        self._init()

    def _init(self):
        self.title = ''
        self.time = ''
        self.src_list = []

    def init_text(self, text):
        self._init()
        title = self.title_regex.search(text)
        time = self.time_regex.search(text)
        self.title = title.group(1) if title else ''
        self.time = time.group(1) if time else ''
        for src in Response(text=text).xpath('//*[@id="js_content"]/p/img/@data-src').extract():
            if bool(self.domain_regex.search(urlparse(src).hostname)):
                self.src_list.append(src)


class Spider:

    def __init__(self, urls, **regex):
        if not isinstance(urls, list):
            urls = [urls]
        self.urls = urls
        self.regex = RegexFilter(**regex)
        self._init()

    def _init(self):
        self.dir_path = ''
        self.src_path = ''
        self.count = count().__next__

    def download(self, url):
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'})
        if response.status_code == 200:
            return response
        print(response.text)
        raise Exception('There may exist some AntiSpider code')

    def ensure_path(self, src=False):
        if src:
            return os.path.join(self.dir_path, str(self.count()))
        else:
            self._init()
            self.dir_path = cur_path('{}_{}'.format(self.regex.time, self.regex.title))
            os.makedirs(self.dir_path, exist_ok=True)

    def run(self):
        for url in self.urls:
            try:
                text = self.download(url).text
                self.regex.init_text(text)
                if self.regex.title and self.regex.time:
                    self.ensure_path()
                    all_src_count = len(self.regex.src_list)
                    print('there is {} Image downloading...'.format(all_src_count))
                    num = 0
                    for src in self.regex.src_list:
                        save_image(self.download(src).content, self.ensure_path(src=True))
                        num += 1
                        show_dynamic_ratio(num, all_src_count)
            except:
                import traceback
                print(traceback.format_exc())
            print('\ndone!')


if __name__ == '__main__':
    urls = [
        'https://mp.weixin.qq.com/s/dCVcDO5XMkacicZXcHkxxQ',
        'https://mp.weixin.qq.com/s/ajztSimZvyu6Pn96iPkoAQ',
        # 'https://mp.weixin.qq.com/s?__biz=MzI4NjM3OTYyNA==&mid=2247484846&idx=1&sn=7067dd79d7a1be9ec1c30078499414b4&chksm=ebdc9ea9dcab17bfb466dca4b54af6e5c7273f838a1ffa159147bd31b93d92d7c613d1b6445a&mpshare=1&scene=1&srcid=&sharer_sharetime=1581133491798&sharer_shareid=ffb59974a347e4abe9dfad7ba2118f74&rd2werd=1#wechat_redirect'
    ]
    spider = Spider(urls)
    spider.run()
