from minitools import next_page, HostFilter


def test_next_page():
    current_page = "https://www.baidu.com/s?ie=UTF-8&wd=test&page=1"
    print(next_page(current_page, 'page=(\d+)'))


def test_HostFilter():
    allow_host = ['www.baidu.com', 'www.google.com', 'www.test.com']
    hfr = HostFilter(*allow_host)

    test_urls = [
        'https://docs.python.org/',
        'http://fanyi.youdao.com/',
        'https://www.liaoxuefeng.com/',
        'https://www.aliyun.com/',
        'https://pypi.org/manage/projects/',
        'https://www.baidu.com/s?ie=UTF-8&wd=test'
    ]

    for url in test_urls:
        print(url, hfr.allow(url))


if __name__ == '__main__':
    """Test Code"""
    # test_next_page()
    # test_HostFilter()
