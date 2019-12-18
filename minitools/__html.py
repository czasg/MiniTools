import xlrd
import xlwt
from parsel import Selector

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

"""


class Cell:

    def __init__(self, text='', rowspan=1, colspan=1):
        self.text = text
        self.rowspan = rowspan
        self.colspan = colspan


class HtmlTable:

    def __init__(self):
        pass
