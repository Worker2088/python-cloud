import time
from typing import Callable


def decorator(func: Callable):
    def wrapper():
        start = time.time()
        res = func()
        end = time.time()
        print(f"время выполнения функции, {end - start}", )
        return res
    return wrapper


@decorator
def my_func():
    time.sleep(2)
    return print(55)

# my_func()

def decorator2(func: Callable):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f"время выполнения функции, {end - start}", )
        return res
    return wrapper


@decorator2
def my_func2(time_sleep: int):
    time.sleep(time_sleep)
    return print(time_sleep)

my_func2(1)