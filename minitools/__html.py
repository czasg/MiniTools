import xlrd
import xlwt
from parsel import Selector

from minitools.scrapy import from_xpath, xt

"""
解析出html格式的table
解析出excel文件中的字段
解析出work文档中的table

requirements:
xlrd
xlwt

需求调研：
针对html中的table，有常见的<table><tbody><th><tr><td>  - 我们这位这种属于正常。还有表格合并，表示为rowspan和colspan
目标是转化为什么呢。table标准的key-value形式。col为key，row为value
0、针对html的标准表格，如何进行转化与解析。
1、现在的需求是要将excel和word中的表格转化为html形式的表格
2、将html形式的表格转化为excel形式的表格
3、将html形式的表格直接一键可视化

必定会出现不友好的合并类表格
需要约定好解析规则。必须以key作为标准。
一个key里面多个col合并，则将其合并为一即可。换行划分即可。
一个key里面多个row合并，则将row拆分为对应数据量的row即可。

恶心的情况：
key占了两到三行，也就是三个row，这玩意怎么合并，是个大问题
"""


class Cell:

    def __init__(self, text='', rowspan=1, colspan=1):
        self.text = text
        self.rowspan = int(rowspan)
        self.colspan = int(colspan)


class RowLine:
    def __init__(self, cols):
        self.cols = [Cell(
            from_xpath(col, ".//text()", xt.string_join),
            from_xpath(col, "./@rowspan") or 1,
            from_xpath(col, "./@colspan") or 1,
        ) for col in cols]

    def set_col(self, index, text):
        # length = len(self)
        # if length <= index:
        #     self.cols += [None] * (index - length + 1)
        # self.cols[index] = Cell(text)
        self.cols.insert(index, Cell(text))

    def __len__(self):
        return len(self.cols)


class HtmlTable:

    def __init__(self, selector, rows):
        self.selector = selector
        self.rows = [RowLine(row.xpath("./*")) for row in rows]
        self.adapter()

    def adapter(self):
        rows = self.rows[:]
        for x, row in enumerate(rows):
            cols = row.cols[:]
            for y, cell in enumerate(cols):
                if cell.rowspan > 1 and cell.colspan > 1:
                    for i in range(cell.rowspan):
                        row = self.rows[x + i]
                        for j in range(cell.colspan):
                            row.set_col(y + j, cell.text)
                elif cell.rowspan > 1:
                    for i in range(cell.rowspan - 1):
                        self.rows[x + i + 1].set_col(y, cell.text)
                elif cell.colspan > 1:
                    for i in range(cell.colspan - 1):
                        row.set_col(y + i + 1, cell.text)

    @classmethod
    def from_html(cls, html):
        selector = _ = Selector(text=html)

        tables = selector.xpath("//table")
        if tables:
            selector = tables[0]

        tbodys = selector.xpath("./tbody")
        if tbodys:
            selector = tbodys[0]

        return cls(_, selector.xpath("./*"))

    @classmethod
    def from_xpath(cls, response, xpath):
        """for scrapy, such as response"""

    def tr_pipe(self, filter_func, res_func=lambda x: x):
        # self.rows[:] = res_func([row for row in self.lengthrows if filter_func(row)])
        return self

    def td_pipe(self, filter_func, res_func=lambda x: x):
        # for row in self.rows:
        #     row.cols[:] = res_func([cell for cell in row.cols if filter_func(cell)])
        return self

    def to_dict(self, default="empty"):
        rows = self.rows
        assert len(rows) > 1, "table rows is too short"
        nums = rows[0].__len__()
        values = []
        for row in rows[1:]:
            length = len(row.cols)
            if length == nums:
                values.append([cell.text for cell in row.cols])
            elif length > nums:
                values.append([cell.text for cell in row.cols[:nums]])
            elif length < nums and default:
                values.append([cell.text for cell in row.cols] + [default] * (nums - length))
            else:
                raise Exception("values in more than keys")

        keys = [col.text for col in rows[0].cols]
        return [dict(zip(keys, value)) for value in values]
