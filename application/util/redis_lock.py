# -*- coding:utf-8 -*-
import time
from application import redis_link as redis
from application import app
if not app.config['DEBUG']:
    from application.util import logger as LOGGER
else:
    from application.util import LocalLogger as LOGGER


class RedisLock(object):
    def __init__(self, key):
        self.redis = redis
        self._lock = 0
        self.lock_key = "auto_test:server:server_{0}_deploy_lock".format(key)

    @staticmethod
    def get_lock(cls, timeout=3):
        while cls._lock != 1:
            timestamp = int(time.time()) + timeout + 1
            cls._lock = cls.redis.setnx(cls.lock_key, timestamp)
            if cls._lock == 1 or (cls.redis.get(cls.lock_key) and
                                  time.time() > float(cls.redis.get(cls.lock_key)) and
                                  time.time() > float(cls.redis.getset(cls.lock_key, timestamp))):
                break
            else:
                time.sleep(0.3)

    @staticmethod
    def release(cls):
        try:
            if cls.redis.exists(cls.lock_key) and not cls.redis.get(cls.lock_key) \
                    and time.time() < float(cls.redis.get(cls.lock_key)):
                cls.redis.delete(cls.lock_key)
        except:
            LOGGER.exception_log('异常键{0}|{1}|是否存在：{2}'.format(cls.lock_key, str(cls.redis.get(cls.lock_key)),
                                                              cls.redis.exists(cls.lock_key)
                                                              ))


def deco(cls):
    def _deco(func):
        def __deco(*args, **kwargs):
            cls.get_lock(cls)
            try:
                return func(*args, **kwargs)
            finally:
                cls.release(cls)
        return __deco
    return _deco





