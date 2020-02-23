import re
import time
import random
import requests

__all__ = ('get_proxy',
           'check_proxy',
           'strip_all',
           'verify_proxy',
           'test_time', 'search_safe',
           'post2json', 'id_pool', 'valid_list',
           'm3u8_to_ts')

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


def valid_list(lis): return list(filter(lambda x: x, lis))


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


def m3u8_to_ts(url: str, download=None):
    assert url.endswith("m3u8")
    text = download(url) if download else requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }).text
    base = re.search('(.*)/', url).group(1)
    for ts in re.findall('(.*?.ts)', text):
        yield f"{base}/{ts}"


def test_time(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        print(time.time() - start)
        return res

    return wrapper


def strip_all(string): return "".join(string.split())


class SafeRegular:

    def __init__(self, pattern, flags):
        self.group_nums = re.compile(pattern, flags).groups

    def group(self, g: int = 0):
        assert 0 <= g <= self.group_nums, "index out of range"
        return None

    def groups(self):
        return (None,) * self.group_nums


def search_safe(pattern, string: str, flags: int = 0):
    res = re.search(pattern, string, flags)
    return res or SafeRegular(pattern, flags)


def post2json(string):
    return ",\n".join(map(lambda x: f'"{x[0].strip()}": "{x[1].strip()}"',
                          map(lambda x: x.split(":", 1),
                              filter(lambda x: x.strip(),
                                     string.strip().split("\n")))))


class SnowFlake:
    def __init__(self, workerId, datacenterId):
        self.workerId = workerId
        self.datacenterId = datacenterId
        self.sequence = 0
        self.twepoch = 1288834974657
        self.workerIdBits = 5
        self.datacenterIdBits = 5
        self.maxWorkerId = -1 ^ (-1 << self.workerIdBits)
        self.maxDatacenterId = -1 ^ (-1 << self.datacenterIdBits)
        self.sequenceBits = 12
        self.workerIdShift = self.sequenceBits
        self.datacenterIdShift = self.sequenceBits + self.workerIdBits
        self.timestampLeftShift = self.sequenceBits + self.workerIdBits + self.datacenterIdBits
        self.sequenceMask = -1 ^ (-1 << self.sequenceBits)
        self.lastTimestamp = -1
        self.get_current_timestamp = lambda: int(time.time() * 1000)

    @classmethod
    def from_node(cls, workerId=0, datacenterId=0):
        return cls(workerId, datacenterId)

    def next_id(self):
        timestamp = self.get_current_timestamp()
        if self.lastTimestamp > timestamp:
            raise Exception()
        if self.lastTimestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequenceMask
            if self.sequence == 0:
                timestamp = self.next_timestamp(timestamp)
        else:
            self.sequence = 0
        self.lastTimestamp = timestamp
        return ((timestamp - self.twepoch) << self.timestampLeftShift) | \
               (self.datacenterId << self.datacenterIdShift) | \
               (self.workerId << self.workerIdShift) | \
               self.sequence

    def next_timestamp(self, timestamp, next_timestamp=0):
        while timestamp >= next_timestamp: next_timestamp = self.get_current_timestamp()
        return next_timestamp


id_pool = SnowFlake.from_node()
