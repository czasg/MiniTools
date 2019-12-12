from minitools.scrapy import miniSpider, from_xpath, xt
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor, FilteringLinkExtractor


class MySpider(miniSpider, CrawlSpider):
    start_urls = ["http://www.klmy.gov.cn/"]
    allowed_domains = ["www.klmy.gov.cn"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 2,
        "DEPTH_LIMIT": 3
    }
    rules = {
        # this rule extract all links which matching your regular, so there will collect links first.
        Rule(link_extractor=LinkExtractor(allow=r"/\d{8}/.*?-.*?-.*?-.*?-.*?\.htm"),
             callback="parse_detail", follow=False, process_request="process_request"),
        # after first extract, the rest of links will be set as `follow=True`
        Rule(link_extractor=LinkExtractor(allow_domains=allowed_domains),
             callback="parse_start_url", follow=True, process_request="process_request"),
    }

    def parse_start_url(self, response):  # No need
        "if next page is not link, you can configure the relevant rules for next_page"

    def process_request(self, request):
        # if you need to polish the request, such as Request.meta['some-config'] = "value"
        return request

    def parse_detail(self, response):
        yield {"url": response.url, "title": from_xpath(response, "//title/text()")}


if __name__ == '__main__':
    MySpider.run(__file__, save=True)
