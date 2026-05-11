"""
Day 3 · Python 进阶练习
======================

完成下面的题目（直接修改本文件）。
完成后运行：python3 day3_练习.py

今天最重要的两题：题 3（装饰器）和题 6（with 语句）。
卡住了回去看 Day3-Python进阶.md。
"""

import time
from functools import wraps
from contextlib import contextmanager
from typing import List, Dict, Optional

print("=" * 50)
print("Day 3 练习")
print("=" * 50)


# ----------------------------------------------------------------------
# 题 1：lambda + sorted（10 分钟）
# ----------------------------------------------------------------------
# 给定用户列表，按下面要求排序：
print("\n--- 题 1：lambda + sorted ---")
users = [
    {"name": "Alice", "age": 30, "salary": 12000},
    {"name": "Bob", "age": 25, "salary": 18000},
    {"name": "Charlie", "age": 35, "salary": 9000},
    {"name": "David", "age": 28, "salary": 15000},
]

# 1.1 按年龄升序排序，打印姓名顺序
# 1.2 按薪资降序排序，打印姓名顺序
# 1.3 按 (年龄升序, 薪资降序) 双关键字排序
# 提示：sorted(list, key=lambda x: ..., reverse=True)
# TODO


# ----------------------------------------------------------------------
# 题 2：高阶函数（10 分钟）
# ----------------------------------------------------------------------
# 实现一个工厂函数 make_adder(n)，
# 返回一个函数，调用时把参数加 n
# 测试：
#   add5 = make_adder(5)
#   print(add5(10))    # 15
#   add10 = make_adder(10)
#   print(add10(20))   # 30
print("\n--- 题 2：高阶函数 ---")
# TODO

# 测试
# add5 = make_adder(5)
# print(add5(10))


# ----------------------------------------------------------------------
# 题 3：装饰器实战（25 分钟）⭐⭐ 重点！
# ----------------------------------------------------------------------
# 3.1 写一个 @timing 装饰器，打印函数耗时
# 要求：
#   - 用 @wraps 保留原函数信息
#   - 处理任意参数（*args, **kwargs）
#   - 输出格式: "[函数名] 耗时 0.0123s"
print("\n--- 题 3.1：@timing 装饰器 ---")

def timing(func):
    # TODO: 实现这个装饰器
    pass

# 测试（不要修改）
# @timing
# def slow_add(a, b):
#     time.sleep(0.5)
#     return a + b
#
# print(slow_add(3, 5))   # 应该打印耗时和结果


# 3.2 写一个带参数的装饰器 @retry(max_times=3)
# 函数报异常时自动重试，超过次数才真正抛出
# 提示：装饰器嵌套三层（func -> wrapper -> 调用）
print("\n--- 题 3.2：@retry 装饰器 ---")

def retry(max_times=3):
    # TODO: 实现这个装饰器
    pass

# 测试（不要修改）
# @retry(max_times=3)
# def unreliable_call():
#     import random
#     if random.random() < 0.7:
#         raise ConnectionError("网络错误")
#     return "成功"
#
# try:
#     print(unreliable_call())
# except Exception as e:
#     print(f"最终失败: {e}")


# ----------------------------------------------------------------------
# 题 4：@property 装饰器（10 分钟）
# ----------------------------------------------------------------------
# 实现一个 Temperature 类：
#   - 内部用 _celsius 存摄氏度
#   - .celsius 属性可读写
#   - .fahrenheit 属性可读写（自动换算 F = C * 9/5 + 32）
#   - 摄氏度低于 -273.15 时抛 ValueError
print("\n--- 题 4：@property ---")

class Temperature:
    pass  # TODO

# 测试（不要修改）
# t = Temperature()
# t.celsius = 25
# print(f"{t.celsius}°C = {t.fahrenheit}°F")  # 25°C = 77.0°F
# t.fahrenheit = 100
# print(f"{t.celsius}°C = {t.fahrenheit}°F")  # 37.78°C 左右


# ----------------------------------------------------------------------
# 题 5：生成器（10 分钟）
# ----------------------------------------------------------------------
# 5.1 写一个生成器函数 fibonacci(n)，生成前 n 个斐波那契数
# 测试：list(fibonacci(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print("\n--- 题 5.1：fibonacci 生成器 ---")

def fibonacci(n):
    # TODO: 用 yield 实现
    pass

# print(list(fibonacci(10)))


# 5.2 用生成器表达式（不是列表推导式）求 1-100 平方和
# 提示：sum(generator_expression)
print("\n--- 题 5.2：生成器表达式 ---")
# TODO


# ----------------------------------------------------------------------
# 题 6：上下文管理器（15 分钟）⭐
# ----------------------------------------------------------------------
# 6.1 用 with open() 写一个文件读写
# 写入 ./test_output.txt 内容 "Hello\nWorld"
# 然后读出来打印
print("\n--- 题 6.1：with open ---")
# TODO


# 6.2 用 @contextmanager 写一个 timer 上下文管理器
# 用法：
#   with timer("数据处理"):
#       time.sleep(0.5)
#       ...
# 输出：
#   [数据处理] 开始
#   [数据处理] 耗时 0.50s
print("\n--- 题 6.2：自定义 with ---")

@contextmanager
def timer(name):
    # TODO
    yield  # 占位

# 测试
# with timer("数据处理"):
#     time.sleep(0.5)


# ----------------------------------------------------------------------
# 题 7：异常处理（10 分钟）
# ----------------------------------------------------------------------
# 写一个安全的除法函数 safe_divide(a, b, default=0)
# - 正常：返回 a / b
# - b 为 0：捕获异常，返回 default
# - 类型错误（如字符串）：捕获异常，返回 default
# 测试：
#   safe_divide(10, 2)        # 5.0
#   safe_divide(10, 0)        # 0
#   safe_divide(10, "abc")    # 0
#   safe_divide(10, 0, -1)    # -1
print("\n--- 题 7：异常处理 ---")

def safe_divide(a, b, default=0):
    pass  # TODO

# 测试
# print(safe_divide(10, 2))
# print(safe_divide(10, 0))
# print(safe_divide(10, "abc"))


# ----------------------------------------------------------------------
# 题 8：类型注解（10 分钟）⭐
# ----------------------------------------------------------------------
# 给下面的函数加完整的类型注解
print("\n--- 题 8：类型注解 ---")

# 8.1 给这个函数加类型注解
def calculate_stats(numbers):
    """返回 {min, max, avg} 三个 float 值"""
    return {
        "min": min(numbers),
        "max": max(numbers),
        "avg": sum(numbers) / len(numbers),
    }

# TODO: 改写上面的函数签名，加上类型注解
# def calculate_stats(numbers: ???) -> ???:


# 8.2 改写下面的函数，加注解
def find_user(users, name):
    """从用户列表里找到指定姓名的用户。找不到返回 None"""
    for u in users:
        if u["name"] == name:
            return u
    return None

# TODO: 加类型注解（提示：用 Optional）


# ----------------------------------------------------------------------
# 题 9：综合实战 - 简易 ORM（20 分钟）⭐⭐
# ----------------------------------------------------------------------
# 实现一个简化版的 ORM 模型基类
# 要求：
#   - 用 dataclass
#   - 子类 User 有 name, age, email 字段
#   - 类方法 from_dict(cls, data) 从字典创建实例
#   - 实例方法 to_dict() 转回字典
#   - 用 @property 加一个 display_name，返回 "name <email>"
print("\n--- 题 9：综合实战 ---")

# TODO: 实现 User 类


# 测试
# data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
# user = User.from_dict(data)
# print(user.display_name)     # "Alice <alice@example.com>"
# print(user.to_dict())        # 应该和 data 一样


print("\n" + "=" * 50)
print("Day 3 练习完成！")
print("如果今天你看 PyTorch 代码不再头大，恭喜你！")
print("=" * 50)
