from minitools.scrapy import miniSpider
from minitools.scrapy import from_xpath, xt


class MySpider(miniSpider):
    name = "test_spider"
    start_urls = ["https://q.cnblogs.com/"]

    def parse(self, response):
        print(from_xpath(response, '//title/text()'))
        print(from_xpath(response, '//title/text()', xt.extract))
        print(from_xpath(response, '//*[@class="one_entity"][1]//text()', xt.string_join))
        print(from_xpath(response, '//*[@class="one_entity"][1]//h2/a/@href', xt.urljoin))
        print(from_xpath(response, '//*[@class="one_entity"][1]', xt.analysis_article))

        alc, new, content = from_xpath(response, [
            '//*[@class="one_entity"]',
            ['.//h2//text()', xt.string_join],
            ['.//h2/a/@href', xt.urljoin, {}, lambda url: url.startswith('https')],

        ])

        for el1, el2 in content:
            print(el1, el2)

        if new:
            yield response.request.replace(url="http://www.czasg.xyz")


if __name__ == '__main__':
    MySpider.run(__file__)
