import json
from datetime import date, datetime

__all__ = "DateEncoder", "load_json", "save_json",


def load_json(path):
    with open(path, 'r') as f:
        return json.loads(f.read())


def save_json(path, json_data, mode="w"):
    with open(path, mode, encoding="utf-8") as f:
        f.write(json.dumps(json_data, ensure_ascii=False))


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return super().default(obj)
