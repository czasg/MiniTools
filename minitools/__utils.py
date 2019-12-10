import re
import random
import requests

__all__ = 'get_proxy', 'check_proxy',

PROXIES = [
    '183.91.33.41:83',
    '183.220.44.23:80',
    '116.247.108.106:8060',
    '1.160.230.95:53281',
    '121.69.46.177:9000',
    '118.126.15.136:8080',
    '116.62.212.97:3128',
    '218.249.69.214:1081',
    '116.114.19.204:443',
    '120.210.219.73:80',
]  # just for test, no mean here.
PROXY_WITHOUT_PROTOCOL = re.compile("(?:https?://)*(.*)").search
VERIFY_URL = "http://httpbin.org/ip"


def get_proxy(): return random.choice(PROXIES)


def check_proxy(proxy): return proxy if proxy.startswith('http') else f"http://{proxy}"


def verify_proxy(proxy):
    proxy = PROXY_WITHOUT_PROTOCOL(proxy).group(1)
    proxies = {protocol: f"{protocol}://{proxy}" for protocol in ["http", "https"]}
    try:
        res = requests.get(VERIFY_URL, proxies=proxies, verify=False)
        if res.status_code == 200:
            print(res.text)
            return True
    except:
        pass
    return False


def test_time(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        print(time.time() - start)
        return res

    return wrapper


if __name__ == '__main__':
    print(test_time(verify_proxy)(get_proxy()))  # 21s
