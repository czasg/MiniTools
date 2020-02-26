import os
import re
import mistune
import subprocess
from minitools import (
    get_current_path, to_path, make_dir, timekiller, make_file, find_file_by_name,
    valid_list, load_json, save_json, create_template
)
from itertools import count
from datetime import datetime
from collections import defaultdict

create_time = lambda file: datetime.fromtimestamp(os.path.getctime(file))
amend_time = lambda file: datetime.fromtimestamp(os.path.getmtime(file))

html_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/3.3.7/css/bootstrap.min.css" />
    <title>$title</title>
</head>
<body style="padding: 30px;">
$body
</body>
</html>
"""


class Path:

    def __init__(self, path):
        self.cur_path = get_current_path(path)
        self.today = timekiller.split()[:3]
        self.path = to_path(self.cur_path, *self.today, forceStr=True)
        self.blog_path = ''

    def create_dir(self, path=None):
        make_dir(path or self.path)

    def create_file(self, path, content=''):
        make_file(path, content)


class Blog:
    default_content = """
<!--
./static/img/dd.jpg
未定义
default title
default abstract
default blog content, please don't use some markdown grammar in first paragraph.
-->

## default title

> default abstract

default blog content, please don't use some
markdown grammar in first paragraph.

you also don't want to show this in web-html.
    """

    def __init__(self):
        self.prefix = "pv_blog"
        self.suffix = ".md"
        self.blogs = []
        self.blog_name = ''

    def init_blog(self):
        self.blog_name = to_path(self.prefix, '_', len(self.blogs) + 1, self.suffix, sep='', forceStr=True)


class BlogManager:
    def __init__(self, path):
        self.pather = Path(path)
        self.bloger = Blog()

    def search_blog(self, path=None):
        self.bloger.blogs = find_file_by_name(self.bloger.prefix, path=(path or self.pather.path),
                                              matching='startswith')

    def init_blog(self):
        self.pather.create_dir()
        self.search_blog()
        self.bloger.init_blog()
        self.pather.blog_path = to_path(self.pather.path, self.bloger.blog_name)

    def create(self):
        self.init_blog()
        self.pather.create_file(self.pather.blog_path, self.bloger.default_content.strip())


class GatherManager:
    def __init__(self, path, html=False):
        self.html = html
        self.handler = BlogManager(path)
        self.gather_blog_dir = "json"
        self.gather_label_dir = "label"
        self.gather_html_dir = "html"
        self.settings = "settings.json"
        self.limit = 6
        self.labels = defaultdict(list)
        self.author = "CzaOrz"
        self.__init()
        self.init_settings()

    def __init(self):
        self.count = count().__next__
        self.blogs = []
        self.blog_total = 0
        self.blog_id = 1

    def init_settings(self):
        self.settings = to_path(self.handler.pather.cur_path, self.settings)
        if not os.path.exists(self.settings):
            self.handler.pather.create_file(
                self.settings,
                to_path('{"blog_url": ', f'"./{self.gather_blog_dir}/blog1.json"',
                        ', "blog_total": 0, "blog_total_page": 0, "blog_last_url": "", "labels": []}', sep=''))
        self.handler.pather.create_dir(to_path(self.handler.pather.cur_path, self.gather_blog_dir))
        self.handler.pather.create_dir(to_path(self.handler.pather.cur_path, self.gather_label_dir))
        if self.html:
            self.handler.pather.create_dir(to_path(self.handler.pather.cur_path, self.gather_label_dir))

    def search_blog(self):
        self.handler.search_blog('.')
        self.blogs = self.handler.bloger.blogs[:]
        self.blog_total = len(self.blogs)

    def json_file(self, file_id=None, label=None):
        if label:
            return f"./{self.gather_label_dir}/{label}/label{file_id or self.blog_id}.json"
        return f"./{self.gather_blog_dir}/blog{file_id or self.blog_id}.json"

    def gather(self, label=None):
        if len(self.blogs) > self.limit:
            self.blogs, blogs = self.blogs[:-self.limit], self.blogs[-self.limit:]
            self._gather(blogs, self.json_file(self.blog_id + 1), label=label)
            self.gather(label)
        else:
            self._gather(label=label)

    def _gather(self, blogs=None, next_url="", label=None):
        results = []
        for blog in (blogs or self.blogs)[::-1]:
            if not label:
                blog_info = valid_list(blog.strip(".").split(os.sep))
                template = {
                    "blog_id": self.count(),
                    "blog_img": "",
                    "blog_title": "",
                    "blog_abstract": "",
                    "blog_author": self.author,
                    "blog_created": timekiller.datetimeStr(create_time(blog)),
                    "blog_amend": timekiller.datetimeStr(amend_time(blog)),
                    "blog_content": "",
                    "blog_url": f"./{to_path(*blog_info, sep='/')}".replace(".md", ""),
                }
                with open(blog, 'r', encoding='utf-8') as f:
                    text = f.readline()
                    assert text.startswith("<!--"), 'Invalid blog-content, it should startswith <!--xxx-->'
                    template['blog_img'] = f.readline().strip()
                    template['labels'] = f.readline().strip().split('|')
                    template['blog_title'] = f.readline().strip()
                    template['blog_abstract'] = f.readline().strip()
                    template['blog_content'] = f.readline().strip()

                    if self.html:
                        f.readline()
                        template["blog_url"] = self._get_html_url(blog_info, template['blog_title'], f.read())

                    results.append(template)
                    for _label in template['labels']:
                        self.labels[_label].append(template)
            else:
                results.append(blog)
        save_json(self.json_file(label=label), {
            "blogs": results,
            "next_url": next_url
        })
        self.blog_id += 1

    def _get_html_url(self, blog_info, title, body):
        self.handler.pather.create_dir(
            to_path(self.gather_html_dir, *blog_info[:3])
        )
        html_path = to_path(self.gather_html_dir, *blog_info, sep='/') \
            .replace(self.handler.bloger.prefix, self.gather_html_dir) \
            .replace(".md", ".html")
        create_template(html_path, html_template, {
            "title": title,
            "body": mistune.markdown(body)
        })
        return html_path

    def save_settings(self):
        settings = load_json(self.settings)
        settings['blog_total'] = self.blog_total
        settings['blog_total_page'] = self.blog_id - 1
        settings['blog_last_url'] = self.json_file(self.blog_id - 1)
        settings['labels'] = []
        for name, templates in self.labels.items():
            settings['labels'].append({
                'name': name,
                'url': f'./{self.gather_label_dir}/{name}/label1.json',
                'total': len(templates),
                'total_page': len(templates) // 6 + 1,
            })
            self.handler.pather.create_dir(to_path(self.gather_label_dir, name))
            self.__init()
            self.blogs[:] = templates
            self.gather(name)
        save_json(self.settings, settings)

    def run(self):
        self.search_blog()
        self.gather()
        self.save_settings()


class MdBlog:
    git_uri = "https://gitee.com/czaOrz/blog.git"

    def __init__(self, path):
        self.path = path

    def create(self):
        BlogManager(self.path).create()

    def gather(self, html=False):
        GatherManager(self.path, html).run()

    def git_clone(self, uri=None):
        dir = re.search('.*/(.*?)\.', uri or self.git_uri).group(1)
        git_dir = to_path(get_current_path(__file__), dir)
        if os.path.exists(git_dir):
            raise Exception(f'{dir} has exists, if you have git clone it?')
        try:
            subprocess.run(f"git clone {self.git_uri}", shell=True)
            assert os.path.exists(git_dir), 'There may exist some mistakes in GIT'
        except:
            import traceback
            print(traceback.format_exc())
