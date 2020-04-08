import os
import glob
import json
import struct


class LifoDiskQueue(object):
    """Persistent LIFO queue."""

    SIZE_FORMAT = ">L"
    SIZE_SIZE = struct.calcsize(SIZE_FORMAT)

    def __init__(self, path):
        self.path = path
        if os.path.exists(path):  # 如果存在，则打开该文件
            self.f = open(path, 'rb+')
            qsize = self.f.read(self.SIZE_SIZE)
            self.size, = struct.unpack(self.SIZE_FORMAT, qsize)
            self.f.seek(0, os.SEEK_END)  # 直接跳转到尾部的意思吗
        else:
            self.f = open(path, 'wb+')  # 不存在文件，则直接新建一个咯
            self.f.write(struct.pack(self.SIZE_FORMAT, 0))
            self.size = 0

    def push(self, string):
        if not isinstance(string, bytes):
            raise TypeError('Unsupported type: {}'.format(type(string).__name__))
        self.f.write(string)  # 首先将字串写入
        ssize = struct.pack(self.SIZE_FORMAT, len(string))  # 然后计算该字串的长度，而且是固定长度的，4字节长度
        self.f.write(ssize)  # 直接
        self.size += 1

    def pop(self):
        if not self.size:
            return
        self.f.seek(-self.SIZE_SIZE, os.SEEK_END)  # 取数据的时候，先跳转到尾部，拿去固定字串
        size, = struct.unpack(self.SIZE_FORMAT, self.f.read())  # 解密字串，拿到真实的数据长度
        self.f.seek(-size - self.SIZE_SIZE, os.SEEK_END)  # 然后跳转到尾部，回到数据长度的初始位置
        data = self.f.read(size)  # 读取固定长度的字串
        self.f.seek(-size, os.SEEK_CUR)  # 然后从当前cur进行一个回退操作，直接完全截断即可。
        self.f.truncate()
        self.size -= 1
        return data

    def close(self):
        if self.size:
            self.f.seek(0)  # 如果存在，则先到文件头部
            self.f.write(struct.pack(self.SIZE_FORMAT, self.size))
        self.f.close()
        if not self.size:
            os.remove(self.path)

    def __len__(self):
        return self.size


class FifoDiskQueue(object):
    """Persistent FIFO queue."""

    szhdr_format = ">L"
    szhdr_size = struct.calcsize(szhdr_format)

    def __init__(self, path, chunksize=100000):
        self.path = path  # 指定当前的路径的 父路径
        if not os.path.exists(path):  # 如果不存在路径则立即创建的意思吗
            os.makedirs(path)
        self.info = self._loadinfo(chunksize)
        self.chunksize = self.info['chunksize']  # 获取块大小
        self.headf = self._openchunk(self.info['head'][0], 'ab+')  # 打开当前路径下的chunk文件，'q%05d'
        self.tailf = self._openchunk(self.info['tail'][0])  # 一样，一个是head一个是tail，啥意思
        os.lseek(self.tailf.fileno(), self.info['tail'][2], os.SEEK_SET)  # 从头开始跳转到offset的位置，原来就是这个意思
        """
        info = {
            'chunksize': chunksize,
            'size': 0,
            'tail': [0, 0, 0],
            'head': [0, 0],
        } 
        """

    def push(self, string):  # 只会修改 head 字段
        if not isinstance(string, bytes):
            raise TypeError('Unsupported type: {}'.format(type(string).__name__))
        hnum, hpos = self.info['head']  # 当前文件的名字 + chunk总量
        hpos += 1  # 位置 +1
        szhdr = struct.pack(self.szhdr_format, len(string))  # 计算数据的长度的密钥。固定四字节长度
        os.write(self.headf.fileno(), szhdr + string)  # 长度密钥+数据
        if hpos == self.chunksize:  # 达到了块的边界，再开一个块的意思咯
            hpos = 0
            hnum += 1
            self.headf.close()
            self.headf = self._openchunk(hnum, 'ab+')
        self.info['size'] += 1
        self.info['head'] = [hnum, hpos]

    def _openchunk(self, number, mode='rb'):
        return open(os.path.join(self.path, 'q%05d' % number), mode)

    def pop(self):
        tnum, tcnt, toffset = self.info['tail']
        if [tnum, tcnt] >= self.info['head']:
            return
        tfd = self.tailf.fileno()
        szhdr = os.read(tfd, self.szhdr_size)
        if not szhdr:
            return
        size, = struct.unpack(self.szhdr_format, szhdr)
        data = os.read(tfd, size)
        tcnt += 1
        toffset += self.szhdr_size + size
        if tcnt == self.chunksize and tnum <= self.info['head'][0]:
            tcnt = toffset = 0
            tnum += 1
            self.tailf.close()
            os.remove(self.tailf.name)
            self.tailf = self._openchunk(tnum)
        self.info['size'] -= 1
        self.info['tail'] = [tnum, tcnt, toffset]
        return data

    def close(self):
        self.headf.close()
        self.tailf.close()
        self._saveinfo(self.info)
        if len(self) == 0:
            self._cleanup()

    def __len__(self):
        return self.info['size']

    def _loadinfo(self, chunksize):
        infopath = self._infopath()  # 获取path下面的'info.json'
        if os.path.exists(infopath):
            with open(infopath) as f:
                info = json.load(f)  # 如果存在'info.json'文件，则加载该文件内部的属性
        else:
            info = {
                'chunksize': chunksize,
                'size': 0,
                'tail': [0, 0, 0],
                'head': [0, 0],
            }  # 否则返回默认值即可
        return info

    def _saveinfo(self, info):
        with open(self._infopath(), 'w') as f:
            json.dump(info, f)

    def _infopath(self):
        return os.path.join(self.path, 'info.json')

    def _cleanup(self):
        for x in glob.glob(os.path.join(self.path, 'q*')):  # 删除该路径下所有q开头的文件
            os.remove(x)
        os.remove(os.path.join(self.path, 'info.json'))  # 删除 info.json 文件
        if not os.listdir(self.path):
            os.rmdir(self.path)


if __name__ == '__main__':
    queue = FifoDiskQueue(os.path.dirname(__file__))
    # for i in [b'123', b'456']:
    #     queue.push(i)
    print(queue.pop())
    queue.close()

    # print('q%05d' % 10)
    # print(struct.pack('>L', len('string')) )

"""如和录制学习视频
从哪开始，或者从哪里开始入手，哪个方向
"""
