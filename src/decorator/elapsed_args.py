"""
elapsed_args.py

此模块包含一个装饰器工厂函数 `elapsed_precison`，用于创建一个装饰器，该装饰器可以计算目标函数的执行时间，并以指定的精度显示。

函数:
    elapsed_precison(precison): 装饰器工厂函数，用于生成计算执行时间的装饰器。
    power_num(num): 计算从 1 到指定数字的平方和。

用法:
    使用 `@elapsed_precison(precison)` 装饰器装饰目标函数，以打印其执行时间，精度由参数 `precison` 指定。
"""
from time import time


def elapsed_precison(precison):
    """
    装饰器工厂函数，用于创建一个装饰器，该装饰器可以计算目标函数的执行时间，并以指定的精度显示。

    参数:
        precison (int): 显示执行时间的精度（小数点后位数）。

    返回:
        function: 一个装饰器函数，用于装饰目标函数。
    """

    def elapsed(target):
        def decorated(*args, **kwargs):
            start = time()
            result = target(*args, **kwargs)
            end = time()
            print(f"Function {target.__name__} took:", round(end - start, precison))
            return result

        return decorated

    return elapsed


@elapsed_precison(1)
def power_num(num):
    """
    计算从 1 到指定数字的平方和。

    参数:
        num (int): 要计算平方和的最大数字。

    返回:
        int: 从 1 到 num 的平方和。
    """
    # start = time()
    total = 0;
    for i in range(1, num + 1):
        total += i ** 2
    # end = time()
    # print(f"Power num took {end - start} seconds")
    return total


if __name__ == '__main__':
    # power_num = elapsed(power_num)
    print(power_num(1000000))
