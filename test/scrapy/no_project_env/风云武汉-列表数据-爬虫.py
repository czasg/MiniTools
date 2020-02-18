# -*- coding: utf8 -*-
# pip install minitools==0.0.10
# pip install -r D:\workplace\MiniTools\requirements.txt --no-build-isolation
import re
import time
import json
from minitools.scrapy import miniSpider
from minitools import tableParser

date_regex = re.compile('(\d+)[^\d]+(\d+)')
int_regex = re.compile('.*?(\d+)')
template = {
    "省": "湖北",
    "市": "武汉",
    "区": "",
    "街道": "",
    "社区": "",
    "公布时间": "",
    "小区": "",
    "发热数": "",
    "集中隔离数": "",
    "居家隔离数": "",
    "密切接触者": "",
    "出院/治愈": "",
    "死亡": "",
    "疑似数": "",
    "确诊数": "",
    "临床确诊数": "",
    "来源图片文件夹": "",
    "来源图片": "",
    "采集人": "",
    "采集时间": "",
    "备注": "",
}


class MySpider(miniSpider):
    start_urls = ["https://mp.weixin.qq.com/s/QFh--NpJLlxMvwjGWjY9Aw"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/79.0.3945.88 Safari/537.36",
    }

    def parse(self, response):
        def _td_pipe(td):
            if not td.text:
                td.text = '0'
            return True

        def _tr_pipe(tr):
            if len(tr) >= 4:
                tr.cols = tr.cols[:4]
                return True

        table = tableParser.create(response, '//*[@id="js_content"]/table') \
            .td_pipe(_td_pipe) \
            .tr_pipe(_tr_pipe)

        # 解析网页table部分
        rows_dict = {}
        rows = []
        last_col_text = ''
        for row in table.rows:
            if row.cols[0].text == row.cols[1].text == row.cols[2].text == row.cols[3].text:
                if rows:
                    rows_dict[last_col_text] = rows[:]
                last_col_text = row.cols[0].text
                rows = []
            else:
                rows.append(row)
        rows_dict[last_col_text] = rows[:]

        def _data_in_transform(data, data_template, key, aim, res):
            if aim in data[key]:
                result = date_regex.search(data[key])
                data[key] = int(result.group(1))
                data_template[res] = int(result.group(2))

        # 解析部分
        results = []
        for area, rows in rows_dict.items():
            table.rows = rows
            for data in table.to_dict():
                data_template = template.copy()
                data_template['区'] = area
                data_template['社区'] = data['小区/社区']
                _data_in_transform(data, data_template, '确诊', '愈', '出院/治愈')
                _data_in_transform(data, data_template, '疑似', '愈', '出院/治愈')
                if '发热' in str(data['疑似']):  # 解析特例
                    data['发热数'] = int_regex.search(data['疑似']).group(1)
                    data['疑似'] = 0
                if '双阳' in str(data['确诊']) and '单阳' in str(data['确诊']):  # 解析特例
                    res = date_regex.search(data['确诊'])
                    data['确诊'] = int(res.group(1)) + int(res.group(2))
                data_template['确诊数'] = int(data['确诊'])
                data_template['疑似数'] = int(data['疑似'])
                data_template['公布时间'] = '2020-' + '-'.join(date_regex.search(data['通报日期']).groups())
                results.append(data_template)

        with open('风云武汉-列表数据_{}.json'.format(int(time.time())), 'w', encoding='utf-8') as f:
            f.write(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    MySpider.run(__file__)
