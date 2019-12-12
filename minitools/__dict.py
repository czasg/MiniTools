__all__ = ('merge_dict', 'merge_dicts')


def merge_dict(dictionary1: dict, dictionary2: dict) -> dict:
    new_dict = dictionary1.copy()
    if dictionary1 and dictionary2:
        for key, value in dictionary2.items():
            if key not in dictionary1:
                new_dict[key] = value
            elif isinstance(value, dict):
                new_dict[key] = merge_dict(dictionary1[key], value)
            elif isinstance(value, list):
                new_dict[key] = list(set(new_dict[key] + value))
    return new_dict


def merge_dicts(*args):
    new_dict = {}
    for arg in args:
        new_dict = merge_dict(arg, new_dict)
    return new_dict
