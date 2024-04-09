import threading
import multiprocessing
from functools import partial


class GxlDynamicThreadPool:
    def __init__(self, ):
        self._threads = []

    def add_thread(self, func: callable, fun_args: list):
        thread = threading.Thread(target=func, args=fun_args)
        self._threads.append(thread)

    def add_task(self, func: callable, fun_args: list):
        self.add_thread(func, fun_args)

    def start(self):
        for thread in self._threads:
            thread.start()
        self._join()

    def _join(self):
        for thread in self._threads:
            thread.join()


class GxlFixedThreadPool:
    def __init__(self, num_threads: int):
        self.pool = multiprocessing.Pool(processes=num_threads)

    def map(self, func: callable,iterable_arg_list:list, other_fun_args: dict):
        """
        要求函数只用第一个参数是遍历list。
        :param func:
        :param fun_args:
        :return:
        """
        partial_my_function = partial(func, **other_fun_args)
        return self.pool.map(partial_my_function, iterable_arg_list)


    def apply_async(self, func: callable, fun_args: list):
        self.pool.apply_async(func, fun_args)

    def add_thread(self, func: callable, fun_args: list):
        self.apply_async(func, fun_args)

    def add_task(self, func: callable, fun_args: list):
        self.apply_async(func, fun_args)

    def start(self):
        self.pool.close()
        self.pool.join()
