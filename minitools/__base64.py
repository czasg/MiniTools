import base64

__all__ = 'base64img',


class Base64img:

    @staticmethod
    def bytes2str(body):
        return base64.b64encode(body).decode()

    @staticmethod
    def str2bytes(string):
        return base64.b64decode(string)

    @staticmethod
    def fix2prefix(obj):
        if isinstance(obj, bytes):
            obj = Base64img.bytes2str(obj)
        if isinstance(obj, str):
            return f"data:image/png;base64,{obj}"
        raise Exception(f"{obj.__class__} Error, A bytes/str is allowed")


base64img = Base64img
