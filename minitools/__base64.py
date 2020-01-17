import base64

__all__ = 'base64img',


class Base64img:

    @staticmethod
    def byte2base64(byte: bytes) -> str:
        return base64.b64encode(byte).decode()

    @staticmethod
    def base642byte(string: str) -> str:
        return base64.b64decode(string)

    @staticmethod
    def fix2prefix(obj):
        if isinstance(obj, bytes):
            obj = Base64img.byte2base64(obj)
        if isinstance(obj, str):
            return f"data:image/png;base64,{obj}"
        raise Exception(f"{obj.__class__} Error, A bytes/str is allowed")


base64img = Base64img
