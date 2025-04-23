"""
elapsed.py

此模块包含一个装饰器函数 `elapsed`，用于计算目标函数的执行时间，并打印结果。

函数:
    elapsed(target): 装饰器函数，用于计算目标函数的执行时间。
    power_num(num): 计算从 1 到指定数字的平方和。

用法:
    使用 `@elapsed` 装饰器装饰目标函数，以打印其执行时间。
"""
from time import time


def elapsed(target):
    """
    装饰器函数，用于计算目标函数的执行时间。

    参数:
        target (function): 被装饰的目标函数。

    返回:
        function: 包装后的函数，执行时会打印目标函数的执行时间。
    """

    def decorated(*args, **kwargs):
        """
        包装函数，计算并打印目标函数的执行时间。

        参数:
            *args: 目标函数的位置参数。
            **kwargs: 目标函数的关键字参数。

        返回:
            Any: 目标函数的返回值。
        """
        start = time()
        result = target(*args, **kwargs)
        end = time()
        print(f"Function {target.__name__} took {end - start} seconds")
        return result

    return decorated


@elapsed
def power_num(num):
    """
    计算从 1 到指定数字的平方和。

    参数:
        num (int): 要计算平方和的最大数字。

    返回:
        int: 从 1 到 num 的平方和。
    """
    total = 0
    for i in range(1, num + 1):
        total += i ** 2
    return total


if __name__ == '__main__':
    print(power_num(1000000))
