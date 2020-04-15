import re

from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser

__all__ = ('next_page', 'getHeaders', 'HostFilter', 'UrlParser')


def next_page(url, rule, step=1, replace=None):
    url = url.replace(*replace) if replace else url
    rule_compile = re.compile(rule)
    if rule_compile.groups == 1:
        rule_compile = re.compile(re.sub('(.*)(\(.*)', '(\\1)\\2', rule))
    assert rule_compile.groups == 2, "Regex Rule, need one/two `()`"
    return rule_compile.sub(lambda x: f'{x.group(1)}{int(x.group(2)) + step}', url)


def getHeaders(text, headers=None, show=False):
    regex = re.compile('\s*(.+?):(.*)').search
    result = headers or {}
    for line in filter(lambda x: x, text.split('\n')):
        key, value = regex(line).groups()
        result[key] = value.strip()
    if show:
        from pprint import pprint
        pprint(result)
    return result


class HostFilter:
    def __init__(self, *allowed_domains):
        allowed_domain_pattern = re.compile("^https?")
        for allowed_domain in allowed_domains:
            assert isinstance(allowed_domain, str), "domain should be an string"
            assert not allowed_domain_pattern.match(allowed_domain), "domain shouldn't be an url"
        self.init_regex(allowed_domains)

    def init_regex(self, allowed_domains):
        domains = [re.escape(ad) for ad in allowed_domains]
        self.regex = re.compile(r'^(.*\.)?{}$'.format('|'.join(domains)))

    def allow(self, url):
        return bool(self.regex.search(urlparse(url).hostname))


class UrlParser(HTMLParser):
    ALL_HREF = re.compile('href="(.*?)"').findall

    def __init__(self):
        super(UrlParser, self).__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href")
        if href and tag == "a":
            self.urls.add(href)

    @classmethod
    def get_links(cls, html, source=None):
        urlSeeker = cls()
        urlSeeker.feed(html)
        return [urljoin(source, url) for url in urlSeeker.urls] if source else urlSeeker.urls

    @classmethod
    def get_href(cls, html):
        return [url for url in cls.ALL_HREF(html)
                if not url.startswith((
                "javascript",
                "#",
            ))]
