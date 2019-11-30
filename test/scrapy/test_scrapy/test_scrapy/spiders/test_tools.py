from minitools.scrapy import miniSpider, from_xpath, xt, next_page_request


class MySpider(miniSpider):
    name = "test_spider"
    start_urls = ["https://q.cnblogs.com/list/unsolved?page=1"]

    def parse(self, response):
        print(from_xpath(response, '//title/text()'))
        print(from_xpath(response, '//title/text()', xt.extract))
        print(from_xpath(response, '//*[@class="one_entity"][1]//text()', xt.string_join))
        print(from_xpath(response, '//*[@class="one_entity"][1]//h2/a/@href', xt.urljoin))
        print(from_xpath(response, '//*[@class="one_entity"][1]', xt.analysis_article))

        alc, new, content = from_xpath(response, [
            '//*[@class="one_entity"]',
            ['.//h2//text()', xt.string_join],
            ['.//h2/a/@href', xt.urljoin, {}, lambda url: not url.startswith('https')],

        ])

        for el1, el2 in content:
            print(el1, el2)

        if new and False:  # there is no mean for False, just don't want to get next page
            yield next_page_request(response, 'page=(\d+)')


if __name__ == '__main__':
    MySpider.run(__file__)
