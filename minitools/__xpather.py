import re
import html

from enum import IntEnum

from .__utils import strip_all

__all__ = ('xt', 'from_xpath')


class XpathType(IntEnum):
    single = 0
    extract = 1
    string_join = 2
    urljoin = 3
    analysis_article = 4


xt = XpathType
P_BR_TR_DIV = re.compile('<p.*?>|</p>|<br.*?>|</br>|<tr.*?>|</tr>|<div.*?>|</div>').sub
EMPTY = re.compile('<.*?>').sub


def single(response, xpath_rule, **kwargs):
    return response.xpath(xpath_rule).extract_first()


def extract(response, xpath_rule, **kwargs):
    return response.xpath(xpath_rule).extract()


def string_join(response, xpath_rule, sep='', **kwargs):
    res = []
    for string in extract(response, xpath_rule):
        value = strip_all(string)
        if value:
            res.append(value)
    return sep.join(res)


def urljoin(response, xpath_rule, source=None, **kwargs):
    urls = [(source or response).urljoin(url) for url in extract(response, xpath_rule)]
    return urls[0] if len(urls) == 1 else urls


def analysis_article(response, xpath_rule, **kwargs):
    return transform_html_to_text(string_join(response, xpath_rule).replace("\r\n", " ").replace("\n", " "))


def transform_html_to_text(html_text):
    return '\n'.join(
        map(lambda x: x.strip(), EMPTY('', P_BR_TR_DIV('\n', html.unescape(html_text))).split('\n'))).strip()


func_map = {
    xt.single: single,
    xt.extract: extract,
    xt.string_join: string_join,
    xt.urljoin: urljoin,
    xt.analysis_article: analysis_article,
}


def from_xpath(response, xpath, type=None, **kwargs):
    if isinstance(xpath, list):  # todo, drop this func
        assert len(xpath) > 1, 'i think you should use xpath without list'
        zero, xpath[:] = xpath[0], xpath[1:]
        response_handler = response.xpath(zero)
        results = []
        for handler in response_handler:
            result = []
            flag = False
            for _xpath in xpath:
                _xpath.extend([None for _ in range(4 - len(_xpath))])
                res = from_xpath(handler, *_xpath[:2], **(_xpath[2] or {}), source=response)
                if callable(_xpath[-1]) and _xpath[-1](res):
                    flag = True
                    break
                result.append(res)
            if flag:
                continue
            results.append(result[0] if len(result) == 1 else result) if result else None
        return len(response_handler), len(results), results
    else:
        return func_map[type or xt.single](response, xpath, **kwargs)
