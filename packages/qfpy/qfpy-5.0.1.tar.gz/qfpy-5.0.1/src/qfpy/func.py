"""
map_funcs：map 多个函数
"""
from typing import Callable, Iterable


def map_funcs(funcs: list[Callable], iterable: Iterable) -> Iterable:
    """
    对给定的可迭代对象应用多个函数。
    
    参数:
    funcs - 一个由函数组成的列表，每个函数都将应用于可迭代对象的每个元素。
    iterable - 一个可迭代对象，其每个元素都将被funcs中的函数依次处理。
    
    返回值:
    返回一个迭代器，其包含应用了所有给定函数后的结果。
    """
    # 遍历函数列表，将每个函数依次应用到可迭代对象上
    for func in funcs:
        iterable = map(func, iterable)
    return iterable


if __name__ == '__main__':
    a = map_funcs([lambda x: x + 1, lambda x: x + 2], [1, 2, 3])
    for i in a:
        print(i)