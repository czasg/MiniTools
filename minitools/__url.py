import re
import typing

from urllib.parse import urlparse

__all__ = ('next_page', 'HostFilter')


def next_page(url, rule, step=1, replace=None):
    url = url.replace(*replace) if replace and re.search(replace[0], url) else url
    rule = re.sub('(.*)(\(.*)', '(\\1)\\2', rule) if rule.count('(') == 1 else None
    return re.sub(rule, lambda x: f'{x.group(1)}{int(x.group(2)) + step}', url)


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
