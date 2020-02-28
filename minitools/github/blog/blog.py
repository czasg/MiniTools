from minitools import (
    get_current_path, to_path, make_dir, timekiller, make_file, find_file_by_name
)
from .template import blog_template


class BlogBase:
    prefix = "pv_blog"
    suffix = ".md"

    def __init__(self):
        self.blog_id = 0
        self.blog_img = ""
        self.blog_title = ""
        self.blog_abstract = ""
        self.blog_author = ""
        self.blog_created = ""
        self.blog_amend = ""
        self.blog_content = ""
        self.blog_url = ""
        self.labels = []

    def to_dict(self):
        return {
            "blog_id": self.blog_id,
            "blog_img": self.blog_img,
            "blog_title": self.blog_title,
            "blog_abstract": self.blog_abstract,
            "blog_author": self.blog_author,
            "blog_created": self.blog_created,
            "blog_amend": self.blog_amend,
            "blog_content": self.blog_content,
            "blog_url": self.blog_url,
            "labels": self.labels
        }


class Blog(BlogBase):
    def __init__(self, file_path):
        self.file_path = file_path
        super(Blog, self).__init__()

    def create_file(self, dir_path, num):
        self.blog_url = to_path(dir_path, f"{self.prefix}_{num}{self.suffix}")
        make_file(self.blog_url, blog_template)


class BlogManager:

    def __init__(self, cur_path):
        self.cur_path = get_current_path(cur_path)
        self.blogs = []

    @property
    def blog_total(self):
        return len(self.blogs)

    def init_blog_dir(self):
        self.today = timekiller.split()[:3]
        self.dir_path = to_path(self.cur_path, *self.today, forceStr=True)
        make_dir(self.dir_path)

    def search_blog(self, path):
        for index, file_path in enumerate(find_file_by_name(BlogBase.prefix, path=path, matching='startswith')):
            blog = Blog(file_path)
            blog.blog_id = index
            self.blogs.append(blog)

    def create(self):
        self.init_blog_dir()
        self.search_blog(self.dir_path)
        blog = Blog(None)
        blog.create_file(self.dir_path, self.blog_total + 1)
        print(f"create {blog.blog_url} success")
