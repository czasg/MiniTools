from minitools import base64img

if __name__ == '__main__':
    ss = "https://czaorz.github.io/ioco/open_source_project/spider_scheduler/scheduler.html\n"
    print(base64img.byte2base64(ss.encode()))
