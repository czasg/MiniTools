import json
from minitools import DateEncoder

try:
    from bson import ObjectId
except:
    raise RuntimeError("Package loss, you need install `bson` such as `pip install bson`")

__all__ = "MongodbEncoder", "jdumps"


class MongodbEncoder(DateEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def jdumps(document, ensure_ascii=False):
    return json.dumps(document, ensure_ascii=ensure_ascii, cls=MongodbEncoder)
