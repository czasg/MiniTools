import re

__all__ = 'next_page',


def next_page(url, rule, step=1, replace=None):
    url = url.replace(*replace) if replace and re.search(replace[0], url) else None
    rule = re.sub('(.*)(\(.*)', '(\\1)\\2', rule) if rule.count('(') == 1 else None
    return re.sub(rule, lambda x: f'{x.group(1)}{int(x.group(2)) + step}', url)
