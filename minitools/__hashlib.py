import _io
import hashlib

from io import BytesIO

__all__ = 'to_md5',


def file2md5(fileObj):
    md5 = hashlib.md5()
    while True:
        d = fileObj.read(8096)
        if not d:
            break
        md5.update(d)
    return md5.hexdigest()


def to_md5(obj):
    if isinstance(obj, _io._IOBase):
        return file2md5(obj)
    elif isinstance(obj, str):
        return file2md5(BytesIO(obj.encode()))
    elif isinstance(obj, bytes):
        return file2md5(BytesIO(obj))
