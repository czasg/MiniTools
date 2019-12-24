from minitools.scrapy import miniSpider


class MySpider(miniSpider):
    start_urls = ["https://www.zhipin.com/c101010100/?query=python&ka=sel-city-101010100"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }

    def parse(self, response):
        yield response.request.replace(url=self.start_urls[0], cookies={
            "__zp_stoken__": "cdcfnvoWtXEQpeTCZRYxCh9OLp446CZlKy9aiqlcS5vwUPUVaT4rJ%2Bx7MpRsUBDhd5SWkPzRRXC1PGT2XxFnW37wkKoqMYGZuicRKtj59FqT0e4tzTbe9GjieJtE47n7VmCN"},
                                       callback=self.parse1)

    def parse1(self, response):
        self.log(response.text)


if __name__ == '__main__':
    MySpider.run(__file__)

"""
['seed=ZyzQl%2BBtWMWQRw3CypvS2Vh6jqwCLNoA7bEEFBXt9XA%3D', 
'name=058ad436', 
'ts=1577195947355', 
'callbackUrl=%2Fc101010100%2F%3Fquery%3Dpython%26ka%3Dsel-city-101010100', 
'srcReferer=https%3A%2F%2Fwww.zhipin.com%2Fweb%2Fcommon%2Fsecurity-check.html%3Fseed%3DZyzQl%252BBtWMWQRw3CypvS2eZKr365k7mX1oNCMtBcyeU%253D%26name%3D058ad436%26ts%3D1577195859011%26callbackUrl%3D%252Fc101010100%252F%253Fquery%253Dpython%2526ka%253Dsel-city-101010100%26srcReferer%3D']

var getQueryString = function(name) {
                        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
                        var r = window.location.search.substr(1).match(reg);
                        if (r != null) return unescape(r[2]);
                        return null;
                    };
"""
