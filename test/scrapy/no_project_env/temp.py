# from minitools.scrapy import miniSpider
#
#
# class MySpider(miniSpider):
#     start_urls = ["https://www.baidu.com/"]
#
#     def parse(self, response):
#         for _ in range(10):
#             yield {"key": "value", "test-key": "test-value"}
#
#
# if __name__ == '__main__':
#     MySpider.run(__file__, save=True)

from minitools.__html import HtmlTable
from pprint import pprint


def test1():
    html = "<table>" \
           "<tbody>" \
           "<tr><td>城市</td><td>工资</td><td>喜欢</td></tr>" \
           "<tr><td>武汉</td><td>1000</td><td>No</td></tr>" \
           "<tr><td>深圳</td><td>3000</td><td>Yes</td></tr>" \
           "<tr><td>杭州</td><td>2000</td><td>Yes</td></tr>" \
           "</tbody>" \
           "</table>"
    t = HtmlTable.from_html(html)
    pprint(t.to_dict())


def test2():
    # todo, 前面第一行加入一些空行，这样就会暴露问题。就需要pipe来过滤一些异常数据
    # todo, key里面的结构有分行，也就是前几行都是表头，这种情况怎么处理
    html = """<table>"
           "<tbody>"
           "<tr><td>城市</td><td>工资</td><td>喜欢</td></tr>"
           "<tr><td>杭州</td><td>2000</td><td>Yes</td></tr>"
           
           "<tr><td>武汉</td><td>1000</td><td rowspan="2">武汉深圳一样的</td></tr>"
           "<tr><td>深圳</td><td>3000</td></tr>"
           
           "<tr><td colspan="3">杭州这一行是一样的</td></tr>"
           
           "<tr><td rowspan="2" colspan="2">cza</td><td>Yes</td></tr>"
           "<tr><td>Yes</td></tr>"
           
           
           "</tbody>"
           "</table>"""

    t = HtmlTable.from_html(html)
    pprint(t.to_dict())


if __name__ == '__main__':
    # test1()
    test2()
