# Day 3 · Python 进阶

> ⏱️ 时间：1.5 小时
> 🎯 目标：能看懂 PyTorch / FastAPI / Spring AI Python 客户端的"高级语法"
> 📋 练习：[`练习/day3_练习.py`](./练习/day3_练习.py)

---

## 0. 心法

> **今天学的不是"高级"，是"必备"。**
>
> 因为 PyTorch、FastAPI、HuggingFace 的代码里**到处都是**装饰器、上下文管理器、生成器。
> 不学这些 = 看代码处处打问号。

---

## 1. 函数是一等公民（10 分钟）

Python 里函数和数据一样，**可以赋值、传递、返回**。

```python
def greet(name):
    return f"Hello, {name}"

# 1. 函数赋值给变量
hello = greet
print(hello("Alice"))         # Hello, Alice

# 2. 函数作为参数（高阶函数）⭐
def apply(func, value):
    return func(value)

print(apply(greet, "Bob"))    # Hello, Bob

# 3. 函数作为返回值
def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier

times3 = make_multiplier(3)
print(times3(10))             # 30
```

> 💡 这就是**闭包**。Java 的 lambda 也是闭包，但 Python 用得更频繁。

### Lambda 表达式（匿名函数）

```python
# 普通函数
def square(x):
    return x * x

# Lambda（一行解决）
square = lambda x: x * x

# 实战：sorted 自定义排序
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
sorted_users = sorted(users, key=lambda u: u["age"])
# [{'name': 'Bob', 'age': 25}, {'name': 'Alice', 'age': 30}]
```

> ⚠️ Lambda 只能写**一个表达式**，复杂逻辑还是用 `def`。

---

## 2. 装饰器（Decorator）⭐⭐⭐ 重点（30 分钟）

### 现象：你天天能在代码里看到的 `@xxx`

```python
@app.route("/")              # FastAPI / Flask
def index(): ...

@dataclass                   # Day 1 学过
class User: ...

@property                    # 让方法变成属性
def name(self): ...

@torch.no_grad()             # PyTorch
def evaluate(): ...
```

**这些 `@xxx` 都是装饰器。**

### 装饰器是什么？

> **装饰器 = 一个"包装"函数的函数**
>
> 它在原函数前后加点料（日志、计时、缓存、权限...），但不改原函数。

### 从 0 到 1 理解

#### 第 1 步：手动包装

```python
def slow_function():
    import time
    time.sleep(1)
    return "done"

# 想测量这个函数耗时
import time
start = time.time()
result = slow_function()
print(f"耗时 {time.time() - start:.2f}s")
```

每次调用都要写 3 行测时间，太麻烦。

#### 第 2 步：把"测时间"封装成函数

```python
def with_timing(func):
    def wrapper():
        start = time.time()
        result = func()
        print(f"耗时 {time.time() - start:.2f}s")
        return result
    return wrapper

# 使用
timed_func = with_timing(slow_function)
timed_func()
```

#### 第 3 步：用装饰器语法糖

```python
@with_timing                  # 等价于 slow_function = with_timing(slow_function)
def slow_function():
    time.sleep(1)
    return "done"

slow_function()               # 自动测时
```

**`@xxx` 就是 `xxx(被装饰函数)` 的语法糖**，仅此而已。

### 完整版装饰器（处理任意参数）

```python
import time
from functools import wraps

def timing(func):
    @wraps(func)              # ⭐ 保留原函数的名字、文档
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.time() - start:.4f}s")
        return result
    return wrapper

@timing
def add(a, b):
    return a + b

@timing
def slow_op():
    time.sleep(0.5)
    return "ok"

add(3, 5)                     # add 耗时 0.0000s
slow_op()                     # slow_op 耗时 0.5005s
```

### 实战常用装饰器

```python
# 1. @property：让方法看起来像属性 ⭐
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14 * self.radius ** 2

c = Circle(5)
print(c.area)                 # 78.5（不需要 c.area()）

# 2. @staticmethod：静态方法（不需要 self）
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

MathUtils.add(3, 5)

# 3. @classmethod：类方法（接收类本身）
class User:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"])      # 工厂方法

User.from_dict({"name": "Alice"})

# 4. functools.lru_cache：自动缓存 ⭐
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

fib(100)                      # 秒回，因为有缓存
```

> 💡 **看 PyTorch 代码经常会有 `@torch.no_grad()`**，意思是"在这个函数里关闭梯度计算"，
> 是个带参数的装饰器。**今天看到不要怕**。

---

## 3. 上下文管理器（with 语句）（15 分钟）

### 现象

```python
with open("file.txt") as f:
    content = f.read()
# 离开 with 块，文件自动关闭
```

### 为什么用 with？

#### Java 的写法（Java 7+ try-with-resources）

```java
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    content = reader.readLine();
}  // 自动关闭
```

#### Python 的 with 等价

```python
with open("file.txt") as f:
    content = f.read()
# f 自动关闭
```

**两边都是同样的"自动管理资源"思想**。

### 常见的 with 应用

```python
# 1. 文件
with open("data.txt", "w") as f:
    f.write("hello")

# 2. 多个资源
with open("a.txt") as fa, open("b.txt") as fb:
    ...

# 3. PyTorch（你以后天天看到）
import torch
with torch.no_grad():         # 关闭梯度计算（推理时省内存）
    output = model(input)

# 4. 数据库连接
with db.connect() as conn:
    conn.execute("...")
```

### 自己写一个上下文管理器（快速版）

```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    import time
    start = time.time()
    print(f"[{name}] 开始")
    yield                     # 这里相当于 with 块的位置
    print(f"[{name}] 耗时 {time.time() - start:.2f}s")

# 使用
with timer("data processing"):
    import time
    time.sleep(1)
# 输出：
# [data processing] 开始
# [data processing] 耗时 1.00s
```

---

## 4. 生成器（Generator）（15 分钟）

### 现象：内存友好的"懒"序列

```python
# 普通方式：一次生成所有
def get_squares(n):
    result = []
    for i in range(n):
        result.append(i * i)
    return result

squares = get_squares(1000000)    # 占大量内存

# 生成器方式：用一个生成一个
def get_squares_gen(n):
    for i in range(n):
        yield i * i               # ⭐ yield 是关键

squares_gen = get_squares_gen(1000000)   # 几乎不占内存

for sq in squares_gen:            # 用一个生成一个
    if sq > 100:
        break
```

### 生成器表达式（语法糖）

```python
# 列表推导式
squares_list = [x * x for x in range(100)]    # 占内存

# 生成器表达式（圆括号）
squares_gen = (x * x for x in range(100))     # 不占内存

# 配合 sum / max 等
total = sum(x * x for x in range(1000000))    # 计算时不存中间结果
```

### 为什么 AI 代码常用？

```python
# PyTorch DataLoader 就是个生成器（迭代器）
for batch_x, batch_y in dataloader:    # 一次只加载一个 batch
    output = model(batch_x)
    ...
# 数据集 100GB 也能跑，因为不一次性加载
```

---

## 5. 异常处理（10 分钟）

### Java vs Python

```java
// Java
try {
    doSomething();
} catch (IOException e) {
    e.printStackTrace();
} catch (Exception e) {
    log.error("error", e);
} finally {
    cleanup();
}
```

```python
# Python
try:
    do_something()
except IOError as e:                   # 注意：except，不是 catch
    print(f"IO error: {e}")
except Exception as e:                 # 多个异常
    print(f"Other error: {e}")
else:
    print("success!")                  # 没异常才执行（Java 没这个）
finally:
    cleanup()
```

### 抛出异常

```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为 0")    # 对应 Java 的 throw
    return a / b
```

### 自定义异常

```python
class MyError(Exception):
    pass

raise MyError("自定义错误")
```

### 实用：Python 的"请求原谅，不是请求许可"

```python
# Java 风格（先检查）
if user is not None and "name" in user:
    name = user["name"]
else:
    name = "Unknown"

# Python 风格（直接用，错了再处理）⭐
try:
    name = user["name"]
except (TypeError, KeyError):
    name = "Unknown"

# 更 Pythonic
name = (user or {}).get("name", "Unknown")
```

---

## 6. 模块与包（10 分钟）

### 项目结构示例

```
my_project/
├── main.py
├── utils.py
├── models/
│   ├── __init__.py        # 标识这是一个 package
│   ├── user.py
│   └── order.py
└── services/
    ├── __init__.py
    └── auth.py
```

### 导入方式

```python
# main.py 里
import utils                              # 整个模块
from utils import some_function           # 部分导入
from models.user import User              # 子包
from models import user                   # 只到包
import numpy as np                        # 改名（看 AI 代码必懂）⭐

# AI 圈三件套
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
```

### 安装第三方包

```bash
# pip：Python 的 Maven
pip install numpy pandas torch

# 装多个（从 requirements.txt）
pip install -r requirements.txt

# 列出已装
pip list
```

### 虚拟环境（强烈推荐）

```bash
# 用 venv
python3 -m venv myenv          # 创建
source myenv/bin/activate      # 激活（Linux/Mac）
pip install xxx                # 装包到这个环境
deactivate                     # 退出

# 或用 conda（你已装）
conda create -n ai python=3.11
conda activate ai
```

---

## 7. 类型注解（Type Hints）（10 分钟）

### 现象：现代 Python 代码到处都是

```python
def greet(name: str, age: int = 18) -> str:
    return f"Hi {name}, you are {age}"
```

### 完整语法

```python
from typing import List, Dict, Optional, Union, Tuple

# 基础类型
name: str = "Alice"
age: int = 30
height: float = 1.75
is_admin: bool = False

# 容器类型
nums: List[int] = [1, 2, 3]
mapping: Dict[str, int] = {"a": 1}

# Python 3.9+ 可以直接用内置（更简洁）
nums: list[int] = [1, 2, 3]
mapping: dict[str, int] = {"a": 1}

# 可选（可能是 None）
def find(name: str) -> Optional[User]:    # 可能返回 User 或 None
    ...

# 联合类型
def process(x: Union[int, float]) -> float:    # 接受 int 或 float
    return x * 1.0

# Python 3.10+ 写法
def process(x: int | float) -> float:
    return x * 1.0

# 函数签名
def train(
    model: nn.Module,
    data: List[Tensor],
    epochs: int = 10
) -> Dict[str, float]:
    ...
```

> 💡 **类型注解只是"提示"，运行时不强制检查**。但 IDE 会用它做补全和警告。
> AI 代码（PyTorch、FastAPI、Spring AI Python 客户端）大量使用，**必须看得懂**。

---

## 8. 重要内置函数速查（5 分钟）

```python
# 数据转换
int("42")                  # 42
str(42)                    # "42"
float("3.14")              # 3.14
list("abc")                # ['a', 'b', 'c']

# 数据操作
len(x)                     # 长度
sum(nums)
min(nums) / max(nums)
sorted(nums)
reversed(nums)

# 过滤 / 映射（推荐用推导式代替）
filter(lambda x: x > 0, nums)         # 用 [x for x in nums if x > 0] 更地道
map(lambda x: x * 2, nums)            # 用 [x * 2 for x in nums]

# 类型检查
isinstance(x, int)
type(x)

# IO
print("...")
input("请输入: ")           # 接收用户输入

# 范围
range(10)                  # 0-9
range(1, 11)               # 1-10
range(0, 100, 5)           # 0,5,10,...,95

# enumerate / zip（你已学过）
```

---

## 📋 今日任务清单

- [ ] 通读本文档，**手敲**至少 10 段代码
- [ ] 重点：**装饰器**和 **with 语句**，必须吃透
- [ ] 完成 [`练习/day3_练习.py`](./练习/day3_练习.py)
- [ ] 写一个 `@timing` 装饰器（练习里有题）
- [ ] 看一段开源 PyTorch 代码（30 分钟），找找今天学的语法

---

## 🎯 自测：今天你应该能...

- [ ] 解释 `@something` 是什么意思
- [ ] 自己写一个简单装饰器（带参数处理）
- [ ] 解释 `with open(...) as f:` 比 `f = open(...)` 好在哪
- [ ] 看到 `def train(x: List[int]) -> Dict[str, float]` 不再懵
- [ ] 看到 `*args, **kwargs` 不再懵

---

## 🔍 推荐看的真实代码

学完今天，去这两个仓库看 5 分钟代码，会觉得"原来都看得懂了"：

- [FastAPI 示例](https://github.com/tiangolo/fastapi/tree/master/docs_src) - 装饰器到处是
- [PyTorch 教程](https://github.com/pytorch/tutorials/blob/main/beginner_source/blitz/cifar10_tutorial.py) - 类型注解 + 上下文 + 类

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 4 · NumPy 基础](./Day4-NumPy基础.md)。
