from redis import StrictRedis

__all__ = "get_redis_client",


class RedisClientCache:
    redisdb = None

    @classmethod
    def get_redis_client(cls, **kwargs):
        if not cls.redisdb:
            cls.redisdb = StrictRedis(**kwargs)
        return cls.redisdb


get_redis_client = RedisClientCache.get_redis_client
