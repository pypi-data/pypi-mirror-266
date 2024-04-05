

import functools
import time
from random import randint


def ttl_cache(ttl, maxsize=128, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.

    Args:
        ttl: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """
    dont_throttle=randint(1,max(ttl,1))
    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            time_time = time.time()
            print(dont_throttle)
            time_time=time_time+ dont_throttle


            return _new(*args, **kwargs, __time_salt=int(time_time / ttl))

        return _wrapped

    return _decorator


if __name__ == '__main__':
    @ttl_cache(100)
    def call_expensive(a: int):
        time.sleep(5)
        return a ** 2
    @ttl_cache(100)
    def call_expensive2(a: int):
        time.sleep(5)
        return a ** 2


    call_expensive(122)
    call_expensive2(122)
    call_expensive(122)
    call_expensive2(122)