from logging import WARNING
from scrapy.exceptions import IgnoreRequest
from minitools.javascript import get_anti_spider_clearance

__all__ = "ANTI_SPIDER_JSL_CLEARANCE_MIDDLEWARE",

ANTI_SPIDER_JSL_CLEARANCE_MIDDLEWARE = {
    'DOWNLOADER_MIDDLEWARES': {
        'minitools.scrapy.downloadermiddlewares.jsl_clearance.JslClearanceCookieMiddleware': 199,
    }
}


class JslClearanceCookieMiddleware:

    def process_response(self, request, response, spider):
        text = response.text
        if text.startswith("<script>") and "__jsl_clearance" in text:
            if '__jsl_clearance' in request.cookies:
                spider.log("Calculate __jsl_clearance value wrong, Ignore this Request", level=WARNING)
                raise IgnoreRequest()
            try:
                key, value = get_anti_spider_clearance(text.strip()).split("=", 1)
                clearance = {key: value}
            except:
                spider.log("Calculate __jsl_clearance error, Ignore this Request", level=WARNING)
                raise IgnoreRequest()
            else:
                return request.replace(dont_filter=True, cookies=clearance)
        return response
