"""
Day 3 · Python 进阶练习
======================

完成下面的题目（直接修改本文件）。
完成后运行：python3 day3_练习.py

今天最重要的两题：题 3（装饰器）和题 6（with 语句）。
卡住了回去看 Day3-Python进阶.md。
"""

from dataclasses import dataclass
import time
from functools import wraps
from contextlib import contextmanager
from typing import Any, List, Dict, Optional

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
print([user["name"] for user in sorted(users, key=lambda u: u["age"])])
print([user["name"] for user in sorted(users, key = lambda u:u["salary"], reverse = True)])
print([user["name"] for user in sorted(users, key = lambda u : (u["age"], -u["salary"]))])


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
def make_adder(factor):
    def adder(x):
        return x + factor
    return adder

# 测试
add5 = make_adder(10)
print(add5(5))


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
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] 耗时：{time.time() - start: .2f}")
        return result
    return wrapper

# 测试（不要修改）
@timing
def slow_add(a, b):
    time.sleep(0.5)
    return a + b

print(slow_add(3, 5))   # 应该打印耗时和结果


# 3.2 写一个带参数的装饰器 @retry(max_times=3)
# 函数报异常时自动重试，超过次数才真正抛出
# 提示：装饰器嵌套三层（func -> wrapper -> 调用）
print("\n--- 题 3.2：@retry 装饰器 ---")

def retry(max_times=3):
    def c(func):
        def w(*args,**kwargs):
            for i in range(max_times):
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    print(f"第{i + 1}次重试 {e}")
            raise Exception(f"重试次数过多 {max_times}")
        return w
    return c


# 测试（不要修改）
@retry(max_times=3)
def unreliable_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络错误")
    return "成功"

try:
    print(unreliable_call())
except Exception as e:
    print(f"最终失败: {e}")


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
    def __init__(self):
        self._celsius = 0
    
    @property
    def celsius(self):
        return self._celsius
    @celsius.setter
    def celsius(self,value):
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9/5 +32

    @fahrenheit.setter
    def fahrenheit(self,value):
        self.celsius = (value - 32) / (9/5)

# 测试（不要修改）
t = Temperature()
t.celsius = 25
print(f"{t.celsius}°C = {t.fahrenheit}°F")  # 25°C = 77.0°F
t.fahrenheit = 100
print(f"{t.celsius}°C = {t.fahrenheit}°F")  # 37.78°C 左右


# ----------------------------------------------------------------------
# 题 5：生成器（10 分钟）
# ----------------------------------------------------------------------
# 5.1 写一个生成器函数 fibonacci(n)，生成前 n 个斐波那契数
# 测试：list(fibonacci(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print("\n--- 题 5.1：fibonacci 生成器 ---")

def fibonacci(n):
    a , b = 0 ,1
    for _ in range(n):
        yield a
        a , b = b , a + b

print(list(fibonacci(10)))


# 5.2 用生成器表达式（不是列表推导式）求 1-100 平方和
# 提示：sum(generator_expression)
print("\n--- 题 5.2：生成器表达式 ---")
print(sum(i * i for i in range(100)))

# ----------------------------------------------------------------------
# 题 6：上下文管理器（15 分钟）⭐
# ----------------------------------------------------------------------
# 6.1 用 with open() 写一个文件读写
# 写入 ./test_output.txt 内容 "Hello\nWorld"
# 然后读出来打印
print("\n--- 题 6.1：with open ---")
with open("./test_output.txt","w+") as f:
    _ = f.write("Hello\nWorld")
    _ = f.seek(0)
    print(f.read())


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
    import time as t
    start = t.time()
    print(f"[{name}] 开始")
    try:
        yield  # yield 之后的代码在 with 块结束后执行
    finally:
        print(f"[{name}] 耗时 {t.time() - start: .2f}s")

# 测试
with timer("数据处理"):
    time.sleep(0.5)


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
    try:
        return a/b
    except (TypeError,ZeroDivisionError):
        return default


# 测试
print(safe_divide(10, 2))
print(safe_divide(10, 0))
print(safe_divide(10, "abc"))
print(safe_divide(10, 0, -1))

# ----------------------------------------------------------------------
# 题 8：类型注解（10 分钟）⭐
# ----------------------------------------------------------------------
# 给下面的函数加完整的类型注解
print("\n--- 题 8：类型注解 ---")

# 8.1 给这个函数加类型注解
def calculate_stats(numbers : list[float]) -> dict[str, float]:
    """返回 {min, max, avg} 三个 float 值"""
    return {
        "min": min(numbers),
        "max": max(numbers),
        "avg": sum(numbers) / len(numbers),
    }

# def calculate_stats(numbers: ???) -> ???:


# 8.2 改写下面的函数，加注解
def find_user(users: list[dict[str, Any]], name: str) -> dict[str,Any] | None:
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

@dataclass
class User:
    name: str
    age: int
    email: str
    @classmethod
    def from_dict(cls,data):
        return cls(name = data["name"], age = data["age"], email = data["email"])
    @property
    def display_name(self):
        return f"{self.name} <{self.email}>"

    def to_dict(self) :
        return {"name": self.name,"age":self.age,"email": self.email}


# 测试
data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
user = User.from_dict(data)
print(user.display_name)     # "Alice <alice@example.com>"
print(user.to_dict())        # 应该和 data 一样


print("\n" + "=" * 50)
print("Day 3 练习完成！")
print("如果今天你看 PyTorch 代码不再头大，恭喜你！")
print("=" * 50)


def computer_gradient(x, y , w, b):
    """
    计算线性回归的梯度
    参数:
        x: 输入特征数组 (shape: m,)
        y: 真实标签数组 (shape: m,)
        w, b: 当前模型参数
    返回:
        dj_dw, dj_db: 代价函数对 w 和 b 的偏导
    """
    m = len(x)
    dj_db = 0
    dj_dw = 0
    for i in range(m):
        f_wb_i = w * x[i] + b
        dj_db_i = (f_wb_i - y[i])
        dj_dw_i = x[i] * (f_wb_i - y[i])
        dj_db += dj_db_i
        dj_dw += dj_dw_i
    dj_db = dj_db / m
    dj_dw = dj_dw / m
    return dj_db, dj_dw


# ============================================================
# 梯度下降可视化 Demo
# ------------------------------------------------------------
# 目标：用上面写好的 computer_gradient，让 (w, b) 从瞎猜的初值
#       一步步滑到最优解，并把整个过程画出来。
#
# 数据：y = 2x + 1（真实关系），加一点点噪声
# 期望：训练完 w ≈ 2.0, b ≈ 1.0
# ============================================================

def compute_cost(x, y, w, b):
    """计算代价函数 J(w, b) = (1/2m) * Σ(w*x[i] + b - y[i])²"""
    m = len(x)
    total = 0.0
    for i in range(m):
        f_wb_i = w * x[i] + b
        total += (f_wb_i - y[i]) ** 2
    return total / (2 * m)


def gradient_descent(x, y, w_init, b_init, alpha, num_iters):
    """
    完整的梯度下降循环
    返回:
        w, b              : 训练完的参数
        history           : 每一步的 (w, b, J) 记录，用于可视化
    """
    w, b = w_init, b_init
    history = []

    for it in range(num_iters):
        # 1. 算当前位置的"坡度"（复用上面的函数，注意返回顺序是 dj_db, dj_dw）
        dj_db, dj_dw = computer_gradient(x, y, w, b)

        # 2. 算当前位置的"高度"（J 值），只是为了记录和画图，训练本身不需要
        J = compute_cost(x, y, w, b)
        history.append((w, b, J))

        # 3. 朝坡度反方向走一小步（核心更新公式）
        w = w - alpha * dj_dw
        b = b - alpha * dj_db

        # 4. 每隔一段时间打印一下进度
        if it % max(1, num_iters // 10) == 0 or it == num_iters - 1:
            print(f"iter {it:4d} | w={w:7.4f}  b={b:7.4f}  J={J:.6f}  "
                  f"|dj_dw|={abs(dj_dw):.4f}")

    return w, b, history


def run_demo():
    # --- 1. 造一份训练数据 y = 2x + 1 + 噪声 ---
    import random
    random.seed(42)
    x = [i * 0.5 for i in range(20)]                       # 0.0, 0.5, 1.0, ..., 9.5
    y = [2.0 * xi + 1.0 + random.uniform(-0.3, 0.3) for xi in x]

    # --- 2. 跑梯度下降 ---
    print("\n" + "=" * 60)
    print("梯度下降可视化 Demo  (真实 w=2.0, b=1.0)")
    print("=" * 60)
    w_final, b_final, history = gradient_descent(
        x, y,
        w_init=0.0, b_init=0.0,   # 瞎猜的初值
        alpha=0.02,               # 学习率
        num_iters=200,
    )
    print(f"\n最终结果: w = {w_final:.4f}, b = {b_final:.4f}  (目标 ≈ 2.0, 1.0)")

    # --- 3. 可视化（没装 matplotlib 就跳过）---
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[提示] 没装 matplotlib，跳过画图。")
        print("       想看动画请执行: pip install matplotlib numpy")
        return

    try:
        import numpy as np
    except ImportError:
        print("\n[提示] 没装 numpy，跳过等高线图。")
        np = None

    ws = [h[0] for h in history]
    bs = [h[1] for h in history]
    Js = [h[2] for h in history]

    fig = plt.figure(figsize=(15, 4))

    # 子图 1：拟合直线 vs 数据点
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.scatter(x, y, c="steelblue", label="训练数据")
    xs_line = [min(x), max(x)]
    # 初始直线（瞎猜）
    ax1.plot(xs_line, [0 * xi + 0 for xi in xs_line],
             "r--", alpha=0.5, label="初始 (w=0,b=0)")
    # 最终直线
    ax1.plot(xs_line, [w_final * xi + b_final for xi in xs_line],
             "g-", linewidth=2, label=f"训练后 (w={w_final:.2f},b={b_final:.2f})")
    ax1.set_xlabel("x"); ax1.set_ylabel("y")
    ax1.set_title("拟合效果")
    ax1.legend(); ax1.grid(alpha=0.3)

    # 子图 2：代价 J 随迭代下降
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.plot(Js, "b-")
    ax2.set_xlabel("迭代次数"); ax2.set_ylabel("代价 J(w,b)")
    ax2.set_title("J 越来越小 → 模型越来越准")
    ax2.grid(alpha=0.3)

    # 子图 3：(w, b) 在 J 等高线上的下山轨迹
    ax3 = fig.add_subplot(1, 3, 3)
    if np is not None:
        # 在 (w, b) 平面上密铺一片，算每个点的 J，画等高线
        w_grid = np.linspace(-0.5, 3.0, 60)
        b_grid = np.linspace(-1.0, 3.0, 60)
        W, B = np.meshgrid(w_grid, b_grid)
        x_arr, y_arr = np.array(x), np.array(y)
        J_grid = np.zeros_like(W)
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                pred = W[i, j] * x_arr + B[i, j]
                J_grid[i, j] = np.mean((pred - y_arr) ** 2) / 2
        cs = ax3.contour(W, B, J_grid, levels=20, cmap="viridis")
        ax3.clabel(cs, inline=True, fontsize=7)

    ax3.plot(ws, bs, "r.-", markersize=3, linewidth=1, label="下山轨迹")
    ax3.scatter([ws[0]], [bs[0]], c="red", s=80, marker="o", label="起点 (0,0)")
    ax3.scatter([ws[-1]], [bs[-1]], c="lime", s=80, marker="*", label="终点")
    ax3.scatter([2.0], [1.0], c="black", s=80, marker="x", label="真实最优")
    ax3.set_xlabel("w"); ax3.set_ylabel("b")
    ax3.set_title("(w,b) 在 J 等高线上下山")
    ax3.legend(fontsize=8); ax3.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("梯度下降可视化.png", dpi=120, bbox_inches="tight")
    print("\n图已保存到: 梯度下降可视化.png")
    plt.show()


if __name__ == "__main__":
    run_demo()