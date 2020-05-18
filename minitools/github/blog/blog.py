import random
import datetime
from minitools import (
    get_current_path, to_path, make_dir, timekiller, make_file, find_file_by_name
)
from .template import blog_template

img_pool = ['https://ae01.alicdn.com/kf/H38d3294e34a44e92b520312a1cce3681s.png',
            'https://ae01.alicdn.com/kf/Hdc8f1b555aea4e389287d2a84331da62i.png',
            'https://ae01.alicdn.com/kf/H08dfe3dbc508453a94e8df05b0d72765I.png',
            'https://ae01.alicdn.com/kf/H84fe3bb85b5547c8b90bcb1a16444be21.png',
            'https://ae01.alicdn.com/kf/H650e812c029e4a8f885593ddff559056k.png',
            'https://ae01.alicdn.com/kf/H80bd56581ad2440c98b1455ab61e548co.png',
            'https://ae01.alicdn.com/kf/H6afaf3902644461a866e1e09bf6004480.png',
            'https://ae01.alicdn.com/kf/H7a9157260a3748e89be24de8399da4cdK.png',
            'https://ae01.alicdn.com/kf/Hfdc2d94a4647408499cac0307c642dafi.png',
            'https://ae01.alicdn.com/kf/H2bfbd8cbeb74440f92b2b445b98aeddbT.png',
            'https://ae01.alicdn.com/kf/H3396ce222efd46788d48f98f2c09ff784.png',
            'https://ae01.alicdn.com/kf/Hf111b2be3fcf4f5681042025bad26905E.png',
            'https://ae01.alicdn.com/kf/Hc80c70315e124ce6853e053333335bbfr.png',
            'https://ae01.alicdn.com/kf/H8542b1cbb010462fbfe9b6749a8959cdb.png',
            'https://ae01.alicdn.com/kf/Haf4d3b0529ba47669bf69c7bfc71a5f1Y.png',
            'https://ae01.alicdn.com/kf/H413f0f5efa724ffe8ae7f450778a07448.png',
            'https://ae01.alicdn.com/kf/H0bdd65cb0b4e4801aa5b2d093defdf4dK.png',
            'https://ae01.alicdn.com/kf/H4acfbe89ed7e48c8ac5498ccb862b5bd8.png',
            'https://ae01.alicdn.com/kf/Hb3505621d84a4f8cb125c2910c6991d5M.png',
            'https://ae01.alicdn.com/kf/Hbe459a22bc004f4e8cd4557223febd27Z.png',
            'https://ae01.alicdn.com/kf/H96b9f137cdc448f8957bddda857d35b39.png',
            'https://ae01.alicdn.com/kf/H096aac2dd76541a4a00a405e6ed8d67eN.png',
            'https://ae01.alicdn.com/kf/H7e040060ce6448c1a90050ba49a1d9ecE.png',
            'https://ae01.alicdn.com/kf/Hd06c682f94bc47839555ee6c0b954163f.png',
            'https://ae01.alicdn.com/kf/H02dd8213a09149a5b8f1aef4fbcb3e98B.png',
            'https://ae01.alicdn.com/kf/H7c75d714388d4c07b602c341693fa6a31.png',
            'https://ae01.alicdn.com/kf/H8e998673bc8b486ca315e89c013a6026F.png',
            'https://ae01.alicdn.com/kf/H46b03db65df345d8915c1d803a9c8b16u.png',
            'https://ae01.alicdn.com/kf/Ha92f087c8f84421e80d0449d2fa77dccl.png',
            'https://ae01.alicdn.com/kf/H65f296663e734788b6d2d5cfbd828fa62.png',
            'https://ae01.alicdn.com/kf/H7a277312d55843d1b963746d6ddde10cC.png',
            'https://ae01.alicdn.com/kf/H0babaa506e534701afbfcf43be15e2e27.png',
            'https://ae01.alicdn.com/kf/Hbc64650c7cb14bedaf0ba3d40b87e26aQ.png',
            'https://ae01.alicdn.com/kf/H7dacf3be3084475ca8ed15daa2f914dej.png',
            'https://ae01.alicdn.com/kf/Had6f56455d994ac3af811723be80ac02F.png',
            'https://ae01.alicdn.com/kf/H78b31e912d92482cbffe0837b4675798I.png',
            'https://ae01.alicdn.com/kf/He75017a01c204550ace3b3d5293d4075y.png',
            'https://ae01.alicdn.com/kf/H0e6c4de75ada4a418e3cdbd2a4f27c40U.png',
            'https://ae01.alicdn.com/kf/H127983aa4ee845f5bb99ef81d1cbb2e2Z.png',
            'https://ae01.alicdn.com/kf/H5b7d744c730749d38c943f30ed10e0330.png']


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
        make_file(self.blog_url, blog_template.format(
            timekiller.datetimeStr(datetime.datetime.now()), random.choice(img_pool)))


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
