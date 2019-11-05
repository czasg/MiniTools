__all__ = "get_anti_spider_yunsuoautojump",


def get_anti_spider_yunsuoautojump(url, params="security_verify_data=313932302c31303830"):
    return {
        "params": params,
        "Cookie": {"srcurl": (lambda string: "".join([hex(ord(s))[2:] for s in string]))(url)},
    }
