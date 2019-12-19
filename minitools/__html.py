import numpy as np

from parsel import Selector
from scrapy.http import Response

from .__xpather import from_xpath, xt

__all__ = "tableParser",


class Cell:

    def __init__(self, text='', rowspan=1, colspan=1):
        self.text = text
        self.rowspan = int(rowspan)
        self.colspan = int(colspan)


class RowLine:
    def __init__(self, cols, sep=""):
        self.cols = [Cell(
            from_xpath(col, ".//text()", xt.string_join, sep=sep),
            from_xpath(col, "./@rowspan") or 1,
            from_xpath(col, "./@colspan") or 1,
        ) for col in cols]

    def set_col(self, index, text):
        length = len(self)
        if length <= index:
            self.cols += [Cell()] * (index - length + 1)
        self.cols.insert(index, Cell(text))

    @classmethod
    def from_cells(cls, cells: list):
        instance = cls([])
        instance.cols = cells
        return instance

    def __len__(self):
        return len(self.cols)


class HtmlTable:

    @classmethod
    def create(cls, selector, xpath="//table", sep=""):
        if isinstance(selector, str):
            selector = _ = Selector(text=selector)
        elif isinstance(selector, (Selector, Response)):
            _ = selector
        else:
            raise Exception(f"{cls.__name__} Not Support {type(selector)}")

        tables = selector.xpath(xpath)
        if tables:
            selector = tables[0]
        tbodys = selector.xpath("./tbody")
        if tbodys:
            selector = tbodys[0]
        return cls(_, selector.xpath("./*"), sep=sep)

    def __init__(self, selector, rows, sep=""):
        self.selector = selector
        self.rows = [RowLine(row.xpath("./*"), sep) for row in rows]
        self.adapter()

    def transpose(self):
        first_row = self.rows[0]
        nums = len(first_row)
        for row in self.rows[1:]:
            length = len(row)
            if length == nums:
                pass
            elif length > nums:
                row.cols[:] = row.cols[:nums]
            elif length < nums:
                row.cols += [Cell()] * (nums - length)
        rows = np.array([row.cols for row in self.rows]).transpose()
        self.rows[:] = [RowLine.from_cells(row) for row in rows]
        return self

    def adapter(self):
        rows = self.rows[:]
        for x, row in enumerate(rows):
            cols = row.cols[:]
            for y, cell in enumerate(cols):
                if cell.rowspan > 1 and cell.colspan > 1:
                    for i in range(cell.rowspan):
                        if i == 0:
                            for i in range(cell.colspan - 1):
                                row.set_col(y + i + 1, cell.text)
                            continue
                        row = self.rows[x + i]
                        for j in range(cell.colspan):
                            row.set_col(y + j, cell.text)
                elif cell.rowspan > 1:
                    for i in range(cell.rowspan - 1):
                        self.rows[x + i + 1].set_col(y, cell.text)
                elif cell.colspan > 1:
                    for i in range(cell.colspan - 1):
                        row.set_col(y + i + 1, cell.text)

    def tr_pipe(self, filter_func, res_func=lambda x: x):
        self.rows[:] = res_func([row for row in self.rows if filter_func(row)])
        return self

    def td_pipe(self, filter_func, res_func=lambda x: x):
        for row in self.rows:
            row.cols[:] = res_func([cell for cell in row.cols if filter_func(cell)])
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

    def to_dict_by_one(self):
        rows = self.rows
        res = dict()
        for row in rows:
            cols = row.cols
            try:
                for index in range(0, len(row), 2):
                    res[cols[index].text] = cols[index + 1].text
            except:
                continue
        return res


tableParser = HtmlTable
