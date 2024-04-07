# endcoding = utf-8
"""
author : vex1023
email :  vex1023@qq.com
各类型的decorator
"""

import signal
import time
import logging

from typing import Callable, Union, Tuple, Any, Type, Literal, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from multiprocessing import Lock, Semaphore
from functools import wraps

__all__ = [
    "retry",
    "timeit",
    "singleton",
    "timeout",
    "async_task",
    "async_map",
    "timer",
    "VXAsyncResult",
]


###################################
# 错误重试方法实现
# @retry(tries, CatchExceptions=(Exception,), delay=0.01, backoff=2)
###################################


class retry:

    def __init__(
        self,
        tries: int,
        cache_exceptions: Union[Type[Exception], Tuple[Type[Exception]]],
        delay: float = 0.1,
        backoff: int = 2,
    ) -> None:
        """重试装饰器

        Arguments:
            tries {int} -- 重试次数
            cache_exceptions {Union[Exception, Tuple[Exception]]} -- 发生错误时，需要重试的异常列表

        Keyword Arguments:
            delay {float} -- 延时时间 (default: {0.1})
            backoff {int} -- 延时时间等待倍数 (default: {2})
        """
        if backoff <= 1:
            raise ValueError("backoff must be greater than 1")

        if tries < 0:
            raise ValueError("tries must be 0 or greater")

        if delay <= 0:
            raise ValueError("delay must be greater than 0")

        if not isinstance(cache_exceptions, (tuple, list)):
            cache_exceptions = (cache_exceptions,)

        self._tries = tries
        self._cache_exceptions = tuple(cache_exceptions)
        self._delay = delay
        self._backoff = backoff

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            mdelay = self._delay
            for i in range(1, self._tries):
                try:
                    return func(*args, **kwargs)
                except self._cache_exceptions as err:
                    logging.error(
                        "function %s(%s, %s) try %s times error: %s\n",
                        func.__name__,
                        args,
                        kwargs,
                        i,
                        err,
                    )
                    logging.warning("Retrying in %.4f seconds...", mdelay)

                    time.sleep(mdelay)
                    mdelay *= self._backoff

            return func(*args, **kwargs)

        return wrapper


###################################
# 计算运行消耗时间
# @timeit
###################################


class timeit:
    """
    计算运行消耗时间
    @timeit(0.5)
    def test():
        time.sleep(1)
    """

    def __init__(self, warnning_time: int = 5) -> None:
        self._warnning_time = warnning_time

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                _start = time.perf_counter()
                return func(*args, **kwargs)
            finally:
                cost = time.perf_counter() - _start
                if cost > self._warnning_time:
                    logging.warning(
                        "function %s(%s,%s) used : %f:.6fms",
                        func.__name__,
                        args,
                        kwargs,
                        cost * 1000,
                    )

        return wrapper


class timer:
    """计时器"""

    def __init__(self, descriptions: str = "", *, warnning: float = 0) -> None:
        self._descriptions = descriptions
        self._start = 0.0
        self._warnning = warnning

    def __enter__(self) -> None:
        self._start = time.perf_counter()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        cost = (time.perf_counter() - self._start) * 1000
        if cost > self._warnning > 0:
            logging.warning(f"{self._descriptions} used : {cost:.2f}ms")
        else:
            logging.info(f"{self._descriptions} used : {cost:.2f}ms")


###################################
# Singleton 实现
# @singleton
###################################


class singleton(object):
    """
    单例
    example::

        @singleton
        class YourClass(object):
            def __init__(self, *args, **kwargs):
                pass
    """

    def __init__(self, cls: Type[Any]) -> None:
        self._instance = None
        self._cls = cls
        self._lock = Lock()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._cls(*args, **kwargs)
        return self._instance


###################################
# 限制超时时间
# @timeout(seconds, error_message='Function call timed out')
###################################


# class TimeoutError(Exception):
#    pass


class timeout:

    def __init__(
        self, seconds: float = 1, *, timeout_msg: str = "Function %s call time out."
    ) -> None:
        self._timeout = seconds
        self._timeout_msg = timeout_msg

        pass

    def __call__(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(self._timeout)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)

        return wrapper

    def _handle_timeout(self, signum: int, frame: Any) -> None:
        raise TimeoutError(
            f"{self._timeout_msg} after {self._timeout *1000}ms,{signum},{frame}"
        )


###################################
# 多线程提交任务
# @async_task()
###################################

_NOSET = object()


class VXAsyncResult:
    def __init__(
        self,
        async_result: Future,
    ) -> None:
        self._future = async_result
        self._result = _NOSET

    def result(self) -> Any:
        """运行结果

        Returns:
            Any -- 运行结果
        """
        if self._result is _NOSET:
            self._result = self._future.result()
        return self._result

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.result(), __name)

    def __str__(self) -> str:
        return str(self.result())

    def __repr__(self) -> str:
        return repr(self.result())


class async_task:
    """
    多线程提交任务
    example::

        @async_task
        def test():
            time.sleep(1)
    """

    __executor__ = ThreadPoolExecutor(thread_name_prefix="async_task")

    def __init__(
        self,
        max_workers: int = 5,
        on_error: Literal["ignore", "raise"] = "raise",
    ) -> None:
        self._semaphore = Semaphore(max_workers)
        self._on_error = on_error

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:

        def semaphore_func(*args: Any, **kwargs: Any) -> Any:
            with self._semaphore:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    logging.error(
                        "async_task error: %s",
                        err,
                        exc_info=True,
                        stack_info=True,
                    )
                    if self._on_error == "raise":
                        raise err from err

                    return None

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> VXAsyncResult:
            fn = self.__executor__.submit(semaphore_func, *args, **kwargs)
            return VXAsyncResult(fn)

        return wrapper

    @property
    def executor(self) -> ThreadPoolExecutor:
        return self.__executor__

    @classmethod
    def set_executor(cls, executor: ThreadPoolExecutor) -> None:
        try:
            cls.__executor__.shutdown()
            cls.__executor__ = executor
        except Exception as err:
            logging.error("set executor error: %s", err, exc_info=True)


def async_map(
    func: Callable[..., Any],
    *iterables: Any,
    timeout: Optional[float] = None,
    chunsize: int = 1,
) -> Any:
    """异步map提交任务

    Arguments:
        func {Callable[..., Any]} -- 运行func

    Returns:
        Any -- 返回值
    """
    return async_task.__executor__.map(
        func, *iterables, timeout=timeout, chunksize=chunsize
    )


if __name__ == "__main__":

    @async_task()
    def test(i: int) -> int:
        print("test", i, end="\n")
        time.sleep(1)
        return i + 1

    results = [test(i) for i in range(10)]
    print([result for result in results])
    with timer("test", warnning=0.5):
        time.sleep(1)
        with timer("test1", warnning=1):
            time.sleep(1)
