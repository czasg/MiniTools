from minitools.scrapy import miniSpider
from scrapy import FormRequest


class MySpider(miniSpider):
    start_urls = ["https://www.lagou.com/jobs/list_python/p-city_215?px=default#filterBox"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }

    form = {
        "first": "true",
        "pn": "1",
        "kd": "python"
    }

    def parse(self, response):
        yield FormRequest(
            f"https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false",
            formdata=self.form, callback=self.parse1)

    def parse1(self, response):
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)
