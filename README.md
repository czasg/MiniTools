## MiniTools

this is tools for python, and is also my work environment, maybe there are some widgets you need


* [scrapy](#scrspy)

### scrapy
1、run scrapy fast and without environment  
```python
from minitools.scrapy import miniSpider

class MySPider(miniSpider):
  start_urls = ['http://www.baidu.com']
  
  def parse(self, response):
    print(response.url)

if __name__ == '__main__':
  MySpider.run(__file__)
```






