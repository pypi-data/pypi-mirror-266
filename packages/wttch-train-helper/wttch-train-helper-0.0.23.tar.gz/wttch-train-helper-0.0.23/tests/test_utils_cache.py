from wth.utils import cache_wrapper


@cache_wrapper(prefix="test_utils_cache")
def cache_1():
    return 1


@cache_wrapper(prefix="test_utils_cache")
def cache_2(a):
    return a


@cache_wrapper(prefix="test_utils_cache")
def cache_3(a=1):
    return {'a': a}


@cache_wrapper(prefix="test_utils_cache")
def cache_4(a, b=2):
    return {'a': a, 'b': b}


cache_1()
cache_2(2)
cache_3(a=3)
cache_4(4, b=4)
