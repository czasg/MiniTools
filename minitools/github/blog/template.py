blog_template = """<!--
https://ae01.alicdn.com/kf/Haf4d3b0529ba47669bf69c7bfc71a5f1Y.png
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

html_template = """<!doctype html>
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
