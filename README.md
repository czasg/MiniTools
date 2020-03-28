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

2、get next pages Request
```python
from minitools.scrapy import next_page_request
class MySpider(miniSpider):
  def parse(self, response):
    yield next_page_request(response, 'page=(\d+)')  # you need fill regex in here
```





