import os
import string

__all__ = "template_get", "template_post", "template_ease",

template_base = """
from minitools.scrapy import miniSpider
{}

class MySpider(miniSpider):
    start_urls = ["$url"]
    {}
    def parse(self, response):
        self.log(response.url)
        self.log(response.status)


if __name__ == '__main__':
    MySpider.run(__file__)
"""


def create_template(file_path, method="GET", url=None, formdata=None):
    assert os.path.exists(file_path), "you may should use `__file__`"
    config = dict()
    config['url'] = url or "https://github.com/CzaOrz"
    if method == "GET":
        config['request'] = "Request"
        config['formdata'] = ""
        config['start_requests'] = "yield Request(url)"
    elif method == "POST":
        config['request'] = "FormRequest"
        config['formdata'] = f"formdata = {formdata or {}}\n"
        config['start_requests'] = "yield FormRequest(url, formdata=self.formdata)"
    elif method == "EASE":
        template_string = template_base.format("", "")
        new_spider_template = string.Template(template_string).substitute(**config).lstrip()
        return _write_template_into_file(file_path, new_spider_template)
    else:
        raise RuntimeError("just support GET/POST")
    template_string = template_base.format(
        """from scrapy import $request\n""",
        """$formdata
    def start_requests(self):
        for url in self.start_urls:
            $start_requests
        """
    )
    new_spider_template = string.Template(template_string).substitute(**config).lstrip()
    return _write_template_into_file(file_path, new_spider_template)


def _write_template_into_file(file_path, new_spider_template):
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(new_spider_template)


def template_get(file_path, url=None):
    create_template(file_path, method="GET", url=url)


def template_post(file_path, url=None, formdata=None):
    create_template(file_path, method="POST", url=url, formdata=formdata)


def template_ease(file_path):
    create_template(file_path, method="EASE")
