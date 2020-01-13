import json
from datetime import date, datetime

try:
    from bson import ObjectId
except:
    raise RuntimeError("Package loss, you need install `bson` such as `pip install bson`")

__all__ = "DateEncoder", "MongodbEncoder", "jdumps"


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return super().default(obj)


class MongodbEncoder(DateEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def jdumps(document, ensure_ascii=False):
    return json.dumps(document, ensure_ascii=ensure_ascii, cls=MongodbEncoder)
