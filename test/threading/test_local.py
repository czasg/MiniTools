import threading

from minitools.threading import minilocal

from threading import current_thread

local = minilocal()


def test(a, b, c):
    local.test1 = a
    local.test2 = b
    import time
    time.sleep(c)
    show()


def show():
    print(f"{id(current_thread())}-{local.test1}-{local.test2}")


if __name__ == '__main__':
    aaa = [
        ['cza', 'good', 3],
        ['heihei', 'yhaha', 6],
        ['heihei123', 'yhaha123', 9]
    ]
    for i in aaa:
        t = threading.Thread(target=test, args=i).start()

    # todo, 开启线程后，最后一个线程知道程序结束前都无法关闭?
