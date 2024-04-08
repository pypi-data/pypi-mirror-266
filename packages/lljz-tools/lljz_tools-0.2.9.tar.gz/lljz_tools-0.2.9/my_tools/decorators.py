# coding=utf-8
import datetime
import threading
import time
from functools import wraps
from logging import Logger
from typing import Callable

from my_tools.log_manager import LogManager


def time_cache(cache_time: float):
    __cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, *args, *tuple(kwargs.items()))
            if key in __cache and time.time() - __cache[key][0] <= cache_time:
                return __cache[key][1]
            res = func(*args, **kwargs)
            __cache[key] = (time.time(), res)
            return res

        return wrapper

    return decorator


_timer_logger = LogManager('timer').get_logger()
_catch_exception_logger = LogManager('catch_exception', log_file=None, error_log_file=None).get_logger()
_debug_logger = LogManager('debug').get_logger()


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _timer_logger.info(f'{func.__name__} start')
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        _timer_logger.info(f'{func.__name__} end. use time {(end - start) * 1000:.4f} ms')
        return res

    return wrapper


def auto_retry(retry=3, interval=1, logger=_catch_exception_logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retry):
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa
                    logger.error(f'[retry]{func.__name__} error: [{e.__class__.__name__}]{str(e)}')
                    time.sleep(interval)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def catch_exception(func=None, /, retry=0, interval=0):
    if func is None:
        return catch_exception(_catch_exception_logger, retry, interval)
    if isinstance(func, Logger):
        def outer(func1):
            if retry:
                func1 = auto_retry(retry, interval, func)(func1)

            @wraps(func1)
            def inner(*args, **kwargs):
                try:
                    return func1(*args, **kwargs)
                except Exception as e:
                    func.exception(f'{func1.__name__} error: [{e.__class__.__name__}]{str(e)}')

            return inner

        return outer
    elif isinstance(func, Callable):
        if retry:
            func = auto_retry(retry, interval, _catch_exception_logger)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _catch_exception_logger.exception(f'{func.__name__} error: [{e.__class__.__name__}]{str(e)}')

        return wrapper
    else:
        raise TypeError("catch_exception的第一个参数应该是函数或日志对象")


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _f_info = func.__name__
        args_str = (*args, *map(lambda x: f"{x[0]}={x[1]}", kwargs.items()))
        _f_info = f'{func.__name__}({", ".join(map(str, args_str))})'
        now = datetime.datetime.now()
        t = time.perf_counter()
        res = func(*args, **kwargs)
        _debug_logger.debug(f'function execute result: \n'
                            f'  execute :  {_f_info}\n'
                            f'   result :  {str(res)[:500]}\n'
                            f' start at :  {now}\n'
                            f'finish at :  {datetime.datetime.now()}\n'
                            f' use time :  {(time.perf_counter() - t) * 1000:.4f} ms')
        return res

    return wrapper


def singleton(cls: str | type = ''):
    _instance = {}
    lock = threading.Lock()
    if isinstance(cls, str):
        def outer(cls_):
            @wraps(cls_)
            def inner(*args, **kwargs):
                # key = (cls_, getattr(cls_, cls, None))
                with lock:
                    key = kwargs.get(cls, (str(args[0]) if args else None))
                    key = (cls_, key)
                    if key not in _instance:
                        _instance[key] = cls_(*args, **kwargs)
                    return _instance[key]

            return inner

        return outer
    else:

        @wraps(cls)
        def wrapper(*args, **kwargs):
            with lock:
                if cls not in _instance:
                    _instance[cls] = cls(*args, **kwargs)
                return _instance[cls]

        return wrapper


if __name__ == '__main__':
    from my_tools.monkey import patch_print

    patch_print()

    @singleton
    class Test:

        def __init__(self, uri: str):
            pass

    t1 = Test('123')
    t2 = Test('1234')
    print(t1 is t2)




    @debug
    def fib(n):
        # if random.random() < 0.5:
        #     raise ValueError('test exception')
        s = 0
        for i in range(n):
            s += i
        return s


    @debug
    def add(a, b):
        return a + b


    fib(n=1000000)
    # time.sleep(4)
    # fib(1000000)
    print('Hello World')
    add(a=100, b=200)
