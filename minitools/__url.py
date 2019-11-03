import re

__all__ = 'next_page',


def next_page(url, rule, step=1, replace=None):
    if replace and re.search(replace[0], url):
        url = url.replace(replace[0], replace[1])
    next_page = re.sub('\(.*\)', str(
        int(re.search(rule, url, re.S).group(1)) + step
    ), rule)
    return re.sub(rule, next_page, url, re.S)
