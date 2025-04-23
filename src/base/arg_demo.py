"""
Python不定长参数 (*args、**kwargs含义)，附使用范例
https://www.cnblogs.com/oddpage/p/16171113.html
"""

def foo(param1, *param2):
    """
    单星号（*）：*agrs
    将所以参数以元组(tuple)的形式导入：
    """
    print(param1)
    print(param2)


foo(1, 2, 3, 4, 5)

print("------------------------------------------------------------")

def bar(param1, **param2):
    """
    双星号（**）：**kwargs
    将参数以字典的形式导入
    """
    print(param1)
    print(param2)


bar(1, a=2, b=3)

print("------------------------------------------------------------")

def foo1(bar, lee):
    print(bar, lee)


l = [1, 2]

# 单星号的另一个用法是解压参数列表：
foo1(*l)

print("------------------------------------------------------------")

def foo2(a, b=10, *args, **kwargs):
    print(a)
    print(b)
    print(args)
    print(kwargs)


foo2(1, 2, 3, 4, e=5, f=6, g=7)
