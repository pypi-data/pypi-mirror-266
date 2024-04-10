from time import time
from functools import wraps
from typing import Callable


def get_time(func: Callable) -> Callable:
    """
    装饰器，方便打印函数的执行时间。
    Args:
        func: 包装的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        ret = func(*args, **kwargs)
        use_time = time() - start_time

        arg_strs = [f'{arg}' for arg in args]
        arg_strs += [f'{k} = {v}' for k, v in kwargs.items()]
        print(f"\"{func.__name__}({', '.join(arg_strs)})\" took {use_time:.4f} seconds to execute.")
        return ret

    return wrapper
