import _io
import hashlib
from functools import partial, reduce
from struct import unpack_from
from io import BytesIO

__all__ = 'to_hash', 'to_md5', 'to_sha1', 'AddressingAlgorithm'


def file2hash(fileObj, hashFunc="md5", byte=False):
    hash_handler = getattr(hashlib, hashFunc)()
    while True:
        d = fileObj.read(8096)
        if not d:
            break
        hash_handler.update(d)
    if byte:
        return hash_handler.digest()
    return hash_handler.hexdigest()


def to_hash(obj, hashFunc="md5", byte=False):
    if isinstance(obj, _io._IOBase):
        return file2hash(obj, hashFunc, byte)
    elif isinstance(obj, str):
        return file2hash(BytesIO(obj.encode()), hashFunc, byte)
    elif isinstance(obj, bytes):
        return file2hash(BytesIO(obj), hashFunc, byte)


def to_md5(obj, byte=False):
    return to_hash(obj, "md5", byte)


def to_sha1(obj, byte=False):
    return to_hash(obj, "sha1", byte)


class AddressingAlgorithm:
    binary_128 = staticmethod(lambda hash_value: partial(int, base=16)(hash_value))
    binary_32 = staticmethod(lambda hash_value: unpack_from(">LLLL", hash_value))

    @classmethod
    def hash(cls, key, hashFunc="md5", byte=False):
        return to_hash(key, hashFunc, byte)

    @classmethod
    def getBinary_128(cls, key, hashFunc="md5"):
        return cls.binary_128(cls.hash(key, hashFunc, False))

    @classmethod
    def getBinary_32(cls, key, hashFunc="md5"):
        return reduce(lambda x, y: x ^ y, cls.binary_32(cls.hash(key, hashFunc, True)))

    @classmethod
    def modulus(cls, hashValue, groups):
        return hashValue % groups

    @classmethod
    def hashAnd_32(cls, hashValue, groups):
        return (hashValue ^ (hashValue >> 16)) & (groups - 1)


if __name__ == '__main__':
    print(f"cza's hashValue is {to_hash('cza')}")