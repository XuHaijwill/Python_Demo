"""
【python】魔术方法大全
https://docs.python.org/zh-cn/reference/datamodel.html#special-method-names
https://www.bilibili.com/video/BV1b84y1e7hG/?spm_id_from=333.337.search-card.all.click&vd_source=c102ec68c51d3f8673e6ec1b0c5f195b
"""


class A:
    def __new__(cls, x):
        print("__new__")
        return super().__new__(cls)

    def __init__(self, x):
        self.x = x
        print("A.__init__")

    def __repr__(self):
        return "<A>"

    # def __del__(self):
    #     print("A.__del__")


out = A(1)
print(repr(A(1)))
print(str(A(1)))


class B:
    def __bytes__(self):
        print("__bytes__")
        return bytes([0, 1])


print(bytes(B()))


class Date:
    def __init__(self, year, month, date):
        self.year = year
        self.month = month
        self.date = date


x = Date(2025, 1, 1)
y = Date(2025, 1, 1)

print(x == y)  # False


class Date2:
    def __init__(self, year, month, date):
        self.year = year
        self.month = month
        self.date = date

    def __eq__(self, other):
        """
        加了eq, hash会被移除
        """
        return (self.year == other.year
                and self.month == other.month
                and self.date == other.date)

    def __hash__(self):
        return hash((self.year, self.month, self.date))


x2 = Date2(2025, 1, 1)
y2 = Date2(2025, 1, 1)

print(x2 == y2)  # True


class GetterDemo:
    def __init__(self):
        self.data = "Hello"

    def __getattr__(self, item):
        print(f"__getattr__{item}")
        return None

    # def __getattribute__(self, item):
    #     print("__getattribute__")
    #     return 2

    def __setattr__(self, key, value):
        print("__setattr__")
        super().__setattr__(key, value)


gt = GetterDemo()
print(gt.data)
print(gt.noexists)
print(gt.__setattr__("data","hello tom"))
print(gt.data)