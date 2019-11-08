from minitools import to_datetime

if __name__ == '__main__':
    s1 = '2019年是一个开心的日子，11月份也是不错的么，8号，不错\n\r\n不错12点呢????开心哦，你呢代号11的傻7'
    print(to_datetime(s1))

    s2 = '20191108041597254265'
    print(to_datetime(s2))
