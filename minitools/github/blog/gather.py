import os
import mistune
from typing import List
from itertools import count
from datetime import datetime
from collections import defaultdict
from minitools import (
    get_current_path, to_path, make_dir, timekiller, make_file,
    valid_list, load_json, save_json, create_template, show_dynamic_ratio
)
from .blog import BlogManager, Blog, BlogBase
from .template import html_template

create_time = lambda file: timekiller.datetimeStr(datetime.fromtimestamp(os.path.getctime(file)))
amend_time = lambda file: timekiller.datetimeStr(datetime.fromtimestamp(os.path.getmtime(file)))


class GatherConfig:
    author = "CzaOrz"

    json_dir = "json"
    label_dir = "label"
    html_dir = "html"
    settings = "settings.json"
    limit = 6

    @classmethod
    def json_file_path(cls, page):
        return f"./{cls.json_dir}/blog{page}.json"

    @classmethod
    def label_file_path(cls, label, page):
        return f"./{cls.label_dir}/{label}/label{page}.json"


class GatherManager:

    def __init__(self, cur_path, html=False):
        self.cur_path = get_current_path(cur_path)
        self.html = html
        self.label = ""
        self.labels = defaultdict(list)
        self.config = GatherConfig
        self.blog_manager = BlogManager(self.cur_path)

    def __init(self):
        self.page = self.blog_manager.blog_total // self.config.limit + 1
        self.count = count(1).__next__

    def save_settings(self):
        if not os.path.exists(self.config.settings):
            make_file(
                self.config.settings,
                to_path('{"blog_url": ', f'"./{self.config.json_dir}/blog1.json"',
                        ', "blog_total": 0, "blog_total_page": 0, "blog_last_url": "", "labels": []}', sep=''))
        settings = load_json(self.config.settings)
        settings['blog_total'] = self.blog_total
        settings['blog_total_page'] = self.blog_total // self.config.limit + 1
        settings['blog_url'] = self.config.json_file_path(settings['blog_total_page'])
        settings['blog_last_url'] = self.config.json_file_path(1)
        settings['labels'] = []
        for name, blogs in self.labels.items():
            total = len(blogs)
            total_page = total // self.config.limit + 1
            settings['labels'].append({
                'name': name,
                'url': self.config.label_file_path(name, total_page),
                'total': total,
                'total_page': total_page,
            })
        save_json(self.config.settings, settings)
        print(f"\n已收集到 {len(self.labels)} 类标签")

    def init_dir(self):
        make_dir(to_path(self.cur_path, self.config.json_dir))
        make_dir(to_path(self.cur_path, self.config.label_dir))
        if self.html:
            make_dir(to_path(self.cur_path, self.config.html_dir))

    def search_blog(self):
        self.blog_manager.search_blog('.')
        self.blog_total = self.blog_manager.blog_total
        self.__init()
        print(f"已查询到 {self.blog_total} 篇博客")

    def gather(self):
        self.init_dir()
        self.search_blog()
        self.gather_loop()
        self.save_settings()
        self.gather_labels()

    def gather_loop(self):
        if self.blog_manager.blog_total > self.config.limit:
            self.blog_manager.blogs, blogs = \
                self.blog_manager.blogs[:-self.config.limit], self.blog_manager.blogs[-self.config.limit:]
            self.read_and_save(blogs, has_url=True)
            self.gather_loop()
        else:
            self.read_and_save(self.blog_manager.blogs)

    def read_and_save(self, blogs: List[Blog], has_url=False):
        if blogs[0].blog_url:
            save_file_path = self.config.label_file_path(self.label, self.page)
            next_url = self.config.label_file_path(self.label, self.page - 1) if has_url else ""
        else:
            save_file_path = self.config.json_file_path(self.page)
            next_url = self.config.json_file_path(self.page - 1) if has_url else ""

        results = []
        for blog in blogs[::-1]:
            if blog.blog_url:
                results.append(blog.to_dict())
                continue
            self.read_blog(blog)
            results.append(blog.to_dict())
            for label in blog.labels:
                self.labels[label].append(blog)
            show_dynamic_ratio(self.count(), self.blog_total)

        save_json(save_file_path, {
            "blogs": results,
            "next_url": next_url
        })
        self.page -= 1

    def read_blog(self, blog):
        blog_info = valid_list(blog.file_path.strip(".").split(os.sep))
        blog.blog_url = f"./{to_path(*blog_info, sep='/')}".replace(".md", "")
        blog.blog_author = self.config.author
        blog.blog_created = create_time(blog.file_path)
        blog.blog_amend = amend_time(blog.file_path)
        with open(blog.file_path, 'r', encoding='utf-8') as f:
            text = f.readline()
            assert text.startswith("<!--"), 'Invalid blog-content, it should startswith <!--xxx-->'
            blog.blog_img = f.readline().strip()
            blog.labels = f.readline().strip().split('|')
            blog.blog_title = f.readline().strip()
            blog.blog_abstract = f.readline().strip()
            blog.blog_content = f.readline().strip()
            if self.html:
                f.readline()
                self.init_html_url(blog_info, blog, f.read())

    def init_html_url(self, blog_info, blog, body):
        make_dir(to_path(self.config.html_dir, *blog_info[:3]))
        blog.blog_url = to_path(self.config.html_dir, *blog_info, sep='/') \
            .replace(BlogBase.prefix, self.config.html_dir) \
            .replace(".md", ".html")
        create_template(blog.blog_url, html_template, {
            "title": blog.blog_title,
            "body": mistune.markdown(body)
        })

    def gather_labels(self):
        num = 1
        for name, blogs in self.labels.items():
            self.label = name
            make_dir(to_path(self.config.label_dir, name))
            self.blog_manager.blogs[:] = blogs[::-1]
            self.__init()
            self.gather_loop()
            show_dynamic_ratio(num, len(self.labels))
            num += 1
