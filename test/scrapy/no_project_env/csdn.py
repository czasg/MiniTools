from minitools.scrapy import miniSpider
from scrapy import Request


class MySpider(miniSpider):
    start_urls = ["https://blog.csdn.net/qq_32969281/article/details/103571605"]
    header = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,und;q=0.8",
        "cache-control": "max-age=0",
        "referer": "https://www.csdn.net/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36",
    }

    def start_requests(self):
        yield Request(self.start_urls[0], headers=self.header,
                      cookies={"acw_sc__v2": "5e002337b5e3b0617f0dd288f142e9039eb921f8"})

    def parse(self, response):
        self.log(response.text)


if __name__ == '__main__':
    # MySpider.run(__file__)

    a= [1,2,3,4]
    # import numpy as np
    import pandas as pd
    # ss = np.array(a)
    s = pd.DataFrame(a).describe()
    print(s)

"""
];(function(

["csKHwqMI", "ZsKJwr8VeAsy", "UcKiN8O/wplwMA==", "JR8CTg==", "YsOnbSEQw7ozwqZKesKUw7kwX8ORIQ==", "w7oVS8OSwoPCl3jChMKhw6HDlsKXw4s/YsOG", "fwVmI1AtwplaY8Otw5cNfSgpw6M=", "OcONwrjCqsKxTGTChsOjEWE8PcOcJ8K6", "U8K5LcOtwpV0EMOkw47DrMOX", "HMO2woHCiMK9SlXClcOoC1k=", "asKIwqMDdgMuPsOKBMKcwrrCtkLDrMKBw64d", "wqImMT0tw6RNw5k=", "DMKcU0JmUwUv", "VjHDlMOHVcONX3fDicKJHQ==", "wqhBH8Knw4TDhSDDgMOdwrjCncOWwphhN8KCGcKqw6dHAU5+wrg2JcKaw4IEJcOcwrRJwoZ0wqF9YgAV", "dzd2w5bDm3jDpsK3wpY=", "w4PDgcKXwo3CkcKLwr5qwrY=", "wrJOTcOQWMOg", "wqTDvcOjw447wr4=", "w5XDqsKhMF1/", "wrAyHsOfwppc", "J3dVPcOxLg==", "wrdHw7p9Zw==", "w4rDo8KmNEw=", "IMKAUkBt", "w6bDrcKQwpVHwpNQwqU=", "d8OsWhAUw7YzwrU=", "wqnCksOeezrDhw==", "UsKnIMKWV8K/", "w4zDocK8NUZv", "c8OxZhAJw6skwqJj", "PcKIw4nCkkVb", "KHgodMO2VQ==", "wpsmwqvDnGFq", "wqLDt8Okw4c=", "w7w1w4PCpsO4wqA=", "wq9FRsOqWMOq", "byBhw7rDm34=", "LHg+S8OtTw==", "wqhOw715dsOH", "U8O7VsO0wqvDvcKuKsOqX8Kr", "Yittw5DDnWnDrA==", "YMKIwqUUfgIk", "aB7DlMODTQ==", "wpfDh8Orw6kk", "w7vCqMOrY8KAVk5OwpnCu8OaXsKZP3DClcKyw6HDrQ==", "wow+w6vDmHpsw7Rtwo98LC7CiG7CksORT8KlW8O5wr3Di8OTHsODeHjDmcKlJsKqVA==", "NwV+", "w7HDrcKtwpJawpZb", "wpQswqvDiHpuw6I=", "YMKUwqMJZQ==", "KH1VKcOqKsK1", "fQ5sFUkkwpI=", "wrvCrcOBR8Kk", "M3w0fQ==", "w6xXwqPDvMOFwo5d"]

"""
