from minitools.scrapy import miniSpider
import re


class MySpider(miniSpider):
    start_urls = [
        "https://wh.58.com/chuzu/?utm_source=market&spm=u-2d2yxv86y3v43nkddh1.BDPCPZ_BT&PGTID=0d100000-0009-e7e5-338e-311b0c001ab9&ClickID=2",
    ]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    }

    def parse(self, response):
        self.log(response.text)
        font = re.search(r'.*?<style>@font-face.*?base64,(.*?) format.*</style>.*', response.text, re.S)
        font = font.group(1).replace("')", '')
        self.log(font)
        # with open("test.ttf", 'wb') as f:
        #     f.write(base64.b64decode(font))


if __name__ == '__main__':
    MySpider.run(__file__)

    # from fontTools.ttLib import TTFont
    #
    # font = TTFont('test.ttf')
    # font.saveXML('ft.xml')
