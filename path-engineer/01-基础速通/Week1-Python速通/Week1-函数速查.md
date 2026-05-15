# Week 1 · Python 函数速查手册

> 本文档汇总 Week1 (Day1 ~ Day5) 练习中**实际使用过**的所有函数/方法，按主题分组。
> 每个条目包含：功能描述、签名、参数、返回值、示例。
> 配套文件：`练习/day1_练习.py` ~ `练习/day5_综合项目.py`

---

## 目录

- [一、内置函数 (Built-in)](#一内置函数-built-in)
- [二、字符串方法](#二字符串方法)
- [三、列表方法](#三列表方法)
- [四、字典方法](#四字典方法)
- [五、集合操作](#五集合操作)
- [六、`collections` 模块](#六collections-模块)
- [七、`functools` 模块](#七functools-模块)
- [八、`contextlib` 模块](#八contextlib-模块)
- [九、`dataclasses` 模块](#九dataclasses-模块)
- [十、`typing` 模块](#十typing-模块)
- [十一、`time` 模块](#十一time-模块)
- [十二、`os` / `json` 模块](#十二os--json-模块)
- [十三、`random` 模块](#十三random-模块)
- [十四、文件 I/O (`open`)](#十四文件-io-open)
- [十五、NumPy 创建数组](#十五numpy-创建数组)
- [十六、NumPy 形状与索引](#十六numpy-形状与索引)
- [十七、NumPy 运算与统计](#十七numpy-运算与统计)
- [十八、NumPy 随机模块 `np.random`](#十八numpy-随机模块-nprandom)
- [十九、NumPy 线性代数 `np.linalg`](#十九numpy-线性代数-nplinalg)
- [二十、内置装饰器与魔术方法](#二十内置装饰器与魔术方法)

---

## 一、内置函数 (Built-in)

### `print(*objects, sep=' ', end='\n')`
打印对象到标准输出。
- `*objects`：要打印的任意多个对象
- `sep`：对象之间的分隔符，默认空格
- `end`：结尾字符，默认换行

```python
print("name =", name, sep=": ")  # name: : fletcher
print("a", "b", end="!")          # a b!
```

### `type(obj)`
返回对象的类型。
- 返回值：`type` 对象，如 `<class 'str'>`

```python
type("hi")     # <class 'str'>
type(3.14)     # <class 'float'>
```

### `len(obj)`
返回容器（list/tuple/dict/set/str/ndarray 等）长度。
- 返回值：`int`

```python
len([1, 2, 3])         # 3
len({"a": 1})          # 1
```

### `range(start, stop[, step])`
生成等差整数序列（**不包含** stop）。
- `start`：起点（默认 0）
- `stop`：终点（不含）
- `step`：步长（默认 1，可负）
- 返回值：`range` 对象（可迭代）

```python
list(range(5))         # [0, 1, 2, 3, 4]
list(range(1, 16))     # 1..15
list(range(0, 10, 2))  # [0, 2, 4, 6, 8]
```

### `enumerate(iterable, start=0)`
给可迭代对象加上索引。
- `start`：索引起始值（默认 0）
- 返回值：迭代器，每次产出 `(index, value)`

```python
for i, name in enumerate(["A", "B"], 1):
    print(i, name)   # 1 A / 2 B
```

### `zip(*iterables)`
把多个可迭代对象按位置打包成元组。
- 返回值：迭代器，每次产出 `(a_i, b_i, ...)`，长度取最短

```python
list(zip([1, 2], ["a", "b"]))  # [(1, 'a'), (2, 'b')]
for n, s in zip(employees, salaries): ...
```

### `min(iterable[, key])` / `max(iterable[, key])`
求最小/最大值。
- `key`：函数，按其返回值比较（如 `key=scores.get`）
- 返回值：原集合中的元素

```python
min([3, 1, 4])                              # 1
max(scores, key=scores.get)                 # 分数最高的 key
max(users, key=lambda u: u["salary"])       # 薪资最高的 user
```

### `sum(iterable[, start=0])`
求和（也支持生成器表达式）。

```python
sum([1, 2, 3])                # 6
sum(s["scores"]["math"] for s in students) / len(students)
sum(i * i for i in range(100))   # 用生成器省内存
```

### `sorted(iterable, *, key=None, reverse=False)`
返回**排序后的新列表**（原对象不变）。
- `key`：排序依据函数
- `reverse`：True 降序

```python
sorted([3, 1, 2])                                         # [1, 2, 3]
sorted(users, key=lambda u: u["age"])                     # 按年龄升序
sorted(users, key=lambda u: u["salary"], reverse=True)    # 薪资降序
sorted(users, key=lambda u: (u["age"], -u["salary"]))     # 多关键字
```

### `set(iterable)`
创建集合（自动去重）。

```python
set([1, 1, 2, 3])    # {1, 2, 3}
len(set(nums))       # 去重后元素个数
```

### `dict(**kwargs)` / `list(iterable)`
类型构造函数。

```python
dict(a=1, b=2)        # {'a': 1, 'b': 2}
list(range(5))        # [0, 1, 2, 3, 4]
list(fibonacci(10))   # 把生成器变 list
```

### `abs(x)`
求绝对值。

```python
abs(-3.14)    # 3.14
abs(dj_dw)    # NumPy 标量也可以
```

---

## 二、字符串方法

### `str.split(sep=None)`
按分隔符切分字符串，返回列表。`sep=None` 时按任意空白切分并自动忽略首尾空白。

```python
"a b c".split()              # ['a', 'b', 'c']
text.split()                 # 拆词
"a,b,c".split(",")           # ['a', 'b', 'c']
```

### `str.upper()` / `str.lower()`
返回大写/小写版本（原字符串不变）。

```python
"hello".upper()              # 'HELLO'
[w.upper() for w in words]
```

### f-string 格式化（PEP 498）
```python
f"{name}"                    # 普通插值
f"{x:.2f}"                   # 保留 2 位小数
f"{x:,.2f}"                  # 千分位 + 2 位小数 → 12,345.67
f"{x:.1f}%"                  # 百分号
f"{i:4d}"                    # 整数右对齐占 4 位
f"{w:7.4f}"                  # 总宽 7，4 位小数
```

---

## 三、列表方法

> 列表的核心操作还包含**索引、切片、推导式**——见下方专题。

### 索引与切片
```python
nums[0]       # 第一个
nums[-1]      # 最后一个
nums[:3]      # 前 3 个
nums[-3:]     # 后 3 个
nums[3:7]     # 索引 3~6
nums[::2]     # 每隔一个
nums[::-1]    # 反转
```

### 列表推导式
```python
[i * i for i in range(20)]                              # 映射
[i for i in nums if i % 2 == 0]                         # 过滤
[(s, c) for s in sizes for c in colors]                 # 笛卡尔积（嵌套）
[f"{s}:优秀" if s >= 80 else f"{s}:良好" for s in arr]  # 三元
```

### 解包（unpacking）
```python
a, b = b, a                  # 交换
first, *middle, last = data  # 星号收集
{**default, **user}          # 字典合并
*args, **kwargs              # 函数收集
```

---

## 四、字典方法

### `dict.get(key, default=None)`
安全取值，键不存在时返回默认值（不会抛 KeyError）。

```python
student_scores.get("Frank", 0)    # 0
```

### `dict.items()` / `dict.keys()` / `dict.values()`
返回视图对象（可迭代）。

```python
for name, score in scores.items(): ...
sum(scores.values()) / len(scores)
```

### 字典推导式
```python
{name: score for name, score in scores.items() if score >= 60}
{name: score + 5 for name, score in scores.items()}
{score: name for name, score in scores.items()}      # 反转 k/v
```

---

## 五、集合操作

| 操作      | 符号  | 含义           |
| --------- | ----- | -------------- |
| 交集      | `&`   | 两边都有       |
| 并集      | `\|`  | 任一边有       |
| 差集      | `-`   | 左边有右边没有 |
| 对称差    | `^`   | 只在一边出现   |

```python
fletcher_skills & job_required        # 交集
fletcher_skills - job_required        # 差集
job_required - fletcher_skills        # 反向差集
```

---

## 六、`collections` 模块

### `Counter(iterable)`
统计元素频次，返回类似 dict 的对象。

```python
from collections import Counter
counter = Counter("aabbbc".split())
counter.most_common(3)    # 取频次最高的前 3：[(item, count), ...]
```

| 方法                   | 作用                       |
| ---------------------- | -------------------------- |
| `most_common(n)`       | 返回前 n 个最常见元素      |
| `Counter.update(it)`   | 增量统计                   |
| `Counter.elements()`   | 按计数展开为迭代器         |

---

## 七、`functools` 模块

### `@wraps(func)`
**装饰器内嵌套 wrapper 时必加**——保留被装饰函数的 `__name__`、`__doc__` 等元信息。

```python
from functools import wraps

def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ...
    return wrapper
```

---

## 八、`contextlib` 模块

### `@contextmanager`
把生成器函数变成 `with` 上下文管理器。`yield` 之前是 `__enter__`，之后是 `__exit__`。

```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    print(f"[{name}] 开始")
    try:
        yield        # with 块内代码在此处执行
    finally:
        print(f"[{name}] 耗时 {time.time() - start:.2f}s")

with timer("数据处理"):
    time.sleep(0.5)
```

---

## 九、`dataclasses` 模块

### `@dataclass`
自动生成 `__init__` / `__repr__` / `__eq__`。声明字段即可。

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
```

---

## 十、`typing` 模块

> Python 3.9+ 起，`list`、`dict` 等内置容器可直接做类型注解，不必再 `from typing import List`。

| 注解            | 含义                              |
| --------------- | --------------------------------- |
| `list[float]`   | 元素是 float 的列表               |
| `dict[str, Any]`| 任意 value 的字典                 |
| `Optional[T]`   | 等价于 `T \| None`                |
| `T \| None`     | Python 3.10+ 写法，更短           |
| `Any`           | 任何类型                          |

```python
def find_user(users: list[dict[str, Any]], name: str) -> dict[str, Any] | None: ...
def calculate_stats(numbers: list[float]) -> dict[str, float]: ...
```

---

## 十一、`time` 模块

### `time.time()`
返回当前 Unix 时间戳（秒，float）。常用于测耗时。

```python
start = time.time()
do_something()
elapsed = time.time() - start
```

### `time.sleep(seconds)`
让当前线程睡眠指定秒数。

```python
time.sleep(0.5)    # 睡 0.5 秒
```

---

## 十二、`os` / `json` 模块

### `os.environ.get(key, default=None)`
读取环境变量。

```python
API_KEY = os.environ.get("DASHSCOPE_API_KEY")
```

### `json.dump(obj, fp, *, ensure_ascii=True, indent=None)`
把 Python 对象序列化为 JSON 写入文件。
- `ensure_ascii=False`：保留中文字符
- `indent=2`：缩进美化

```python
with open("out.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

| 函数              | 作用                            |
| ----------------- | ------------------------------- |
| `json.dump`       | 对象 → 文件                     |
| `json.dumps`      | 对象 → 字符串                   |
| `json.load`       | 文件 → 对象                     |
| `json.loads`      | 字符串 → 对象                   |

---

## 十三、`random` 模块

```python
import random

random.seed(42)             # 固定随机种子（可复现）
random.random()             # [0, 1) 浮点
random.uniform(-0.3, 0.3)   # [a, b] 浮点
random.randint(1, 10)       # [1, 10] 整数（含两端）
random.choice([1, 2, 3])    # 随机选一个
```

---

## 十四、文件 I/O (`open`)

### `open(file, mode='r', encoding=None)`
打开文件。**强烈建议配合 `with` 使用**，自动关闭。

| mode    | 含义                         |
| ------- | ---------------------------- |
| `'r'`   | 只读（默认）                 |
| `'w'`   | 写入（覆盖原文件）           |
| `'a'`   | 追加                         |
| `'w+'`  | 读写（先清空）               |
| `'r+'`  | 读写（不清空）               |
| `'b'`   | 二进制后缀，如 `'rb'`/`'wb'` |

### 文件对象常用方法
```python
f.write(text)         # 写入字符串，返回写入字符数
f.read()              # 读全部
f.readline()          # 读一行
f.readlines()         # 读所有行 → list
f.seek(offset)        # 移动指针，0 表示开头
```

```python
with open("./test.txt", "w+") as f:
    f.write("Hello\nWorld")
    f.seek(0)
    print(f.read())
```

---

## 十五、NumPy 创建数组

```python
import numpy as np
```

| 函数                                      | 作用                                  | 示例                                  |
| ----------------------------------------- | ------------------------------------- | ------------------------------------- |
| `np.array(obj)`                           | 从 Python 列表创建                    | `np.array([1, 2, 3])`                 |
| `np.zeros(shape)`                         | 全 0 数组                             | `np.zeros((3, 3))`                    |
| `np.ones(shape)`                          | 全 1 数组                             | `np.ones((5, 5))`                     |
| `np.eye(n)`                               | n×n 单位矩阵                          | `np.eye(3)`                           |
| `np.arange(start, stop, step)`            | 类似 range，可浮点                    | `np.arange(0, 1, 0.1)`                |
| `np.linspace(start, stop, num)`           | 等分 num 个点（**含两端**）           | `np.linspace(0, 1, 11)`               |
| `np.diag(M)`                              | 取/构造对角线                         | `np.diag(M)`                          |

```python
np.array([1, 2, 3])               # [1 2 3]
np.zeros((3, 3))                  # 3×3 全 0
np.eye(5)                         # 5×5 单位矩阵
np.arange(24)                     # [0..23]
np.linspace(0, 1, 11)             # [0.0, 0.1, ..., 1.0]
```

> **`arange` vs `linspace`**：前者按步长，后者按段数。

---

## 十六、NumPy 形状与索引

### 形状操作

| 方法                            | 作用                                    |
| ------------------------------- | --------------------------------------- |
| `.shape`                        | 返回形状元组                            |
| `.reshape(new_shape)`           | 改形状（不改数据），传 `-1` 自动推算    |
| `.T`                            | 转置                                    |
| `.flatten()`                    | 拉平为 1D                               |
| `.sum()` 等的 `axis=` 参数      | 沿哪个轴聚合                            |

```python
a = np.arange(24)
a.shape                  # (24,)
a.reshape(4, 6).shape    # (4, 6)
a.reshape(-1, 6).shape   # (4, 6)，-1 表示让 numpy 自动算
a.reshape(2, 3, 4)       # 三维
M.T                      # 转置
M.flatten()              # 拉成 1D
```

### 索引与切片
```python
M[0]                  # 第 0 行
M[-1]                 # 最后一行
M[:, 1]               # 第 1 列（所有行）
M[:, -1]              # 最后一列
M[-2:, -2:]           # 右下角 2×2 子矩阵
M[1:4, 1:4]           # 中心 3×3
np.diag(M)            # 对角线
```

### 布尔索引
```python
scores[scores >= 60]              # 取出满足条件的元素
scores[scores < 60] = 0           # 条件赋值
(p == true_labels).mean()         # 准确率（True=1, False=0）
```

### `np.where(cond, x, y)`
按条件二选一，返回与 cond 同形数组。
```python
np.where(scores >= 90, 'A', 'B')   # 条件为真取 'A'，否则取 'B'
```

---

## 十七、NumPy 运算与统计

### 算术
```python
A + B          # 逐元素加（同形或可广播）
A * B          # 逐元素乘
A @ B          # 矩阵乘（推荐）
A.dot(B)       # 矩阵乘的方法形式
np.dot(a, b)   # 一维向量时是点积
np.exp(x)      # e^x，逐元素
```

### 聚合（带 axis 参数）

| 方法            | 作用                          |
| --------------- | ----------------------------- |
| `.sum()`        | 求和                          |
| `.mean()`       | 平均                          |
| `.std()`        | 标准差                        |
| `.min()` `.max()` | 最值                        |
| `.argmin()` `.argmax()` | **最值的索引**          |

`axis` 含义：
- `axis=0` → **沿行方向**聚合（按列），结果 shape 少了第 0 维
- `axis=1` → **沿列方向**聚合（按行），结果 shape 少了第 1 维
- `keepdims=True` → 保留维度（便于广播）

```python
A.sum()                          # 全部元素和（标量）
A.sum(axis=0)                    # 每列的和  shape: (3,)
A.sum(axis=1)                    # 每行的和  shape: (3,)
data.mean(axis=0)                # 每列均值
data.std(axis=0)                 # 每列标准差
x_i.sum(axis=1, keepdims=True)   # 保留维度，便于广播除法
```

### `np.argmax(a)` / `np.argmin(a)`
返回**展平后**最值的索引（int）。多维情况一般配合 `np.unravel_index` 还原成下标元组。

```python
np.argmax(A)                                  # 9（展平后位置）
np.unravel_index(np.argmax(A), A.shape)       # (2, 2)
np.argmax(logits, axis=1)                     # 每行最大值的列索引
```

### 广播 (Broadcasting)
两个数组形状不一致时，NumPy 会自动**对齐拉伸**——前提是从右往左每一维要么相等要么有一边为 1。

```python
M2 = np.arange(12).reshape(3, 4)   # (3, 4)
v  = np.array([10, 20, 30, 40])    # (4,)
M2 + v                             # v 自动复制成 (3, 4)

# 经典：标准化（每列减均值除标准差）
(data - data.mean(axis=0)) / data.std(axis=0)

# softmax
exp_x = np.exp(logits)
exp_x / exp_x.sum(axis=1, keepdims=True)
```

---

## 十八、NumPy 随机模块 `np.random`

```python
np.random.seed(42)               # 固定随机种子
np.random.rand(3, 4)             # [0,1) 均匀分布的 (3,4)
np.random.randn(5, 6)            # 标准正态 N(0,1)
np.random.randint(0, 100, 10)    # [0, 100) 整数 10 个
np.random.randint(0, 3, 100)     # 100 个 [0, 3) 的整数标签
```

| 函数                            | 分布            | 备注                      |
| ------------------------------- | --------------- | ------------------------- |
| `np.random.rand(*shape)`        | [0,1) 均匀      | 直接传维度，不用 tuple    |
| `np.random.randn(*shape)`       | 标准正态        | 同上                      |
| `np.random.randint(low, high, size)` | [low, high) 整数 | size 可为 int 或 tuple |
| `np.random.seed(n)`             | 设种子          | 保证可复现                |

> **`rand` vs `randn`**：`rand` 是 0~1 均匀；`randn` 是标准正态（均值 0、方差 1，可能负）。

---

## 十九、NumPy 线性代数 `np.linalg`

### `np.linalg.norm(x)`
默认计算 L2 范数（向量长度）。

```python
np.linalg.norm(np.array([3, 4]))   # 5.0

# 余弦相似度
cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## 二十、内置装饰器与魔术方法

### `@property` / `@<name>.setter`
把方法包装成属性访问。
```python
class Temperature:
    @property
    def celsius(self):           # 读：t.celsius
        return self._celsius

    @celsius.setter
    def celsius(self, value):    # 写：t.celsius = 25
        if value < -273.15:
            raise ValueError("低于绝对零度")
        self._celsius = value
```

### `@classmethod`
第一个参数是 `cls`（类本身），可访问类属性 / 实例化。
```python
@classmethod
def from_dict(cls, data):
    return cls(name=data["name"], age=data["age"])
```

### `@staticmethod`
不接收 `self`/`cls`，只是放在类命名空间下的普通函数。

### 常用魔术方法

| 方法                       | 作用                                       |
| -------------------------- | ------------------------------------------ |
| `__init__(self, ...)`      | 构造函数                                   |
| `__str__(self)`            | `print(obj)` 或 `str(obj)` 时调用          |
| `__repr__(self)`           | 交互式直接打 obj 时调用 / 调试输出         |
| `__len__(self)`            | 让 `len(obj)` 工作                         |
| `__eq__(self, other)`      | `==` 比较                                  |

```python
class BankAccount:
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self.balance = initial_balance

    def __str__(self):
        return f"BankAccount(owner={self.owner}, balance={self.balance})"
```

---

## 附录 A · 装饰器写法模板

### 1. 不带参数装饰器（两层）
```python
def deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

@deco
def f(): ...
```

### 2. 带参数装饰器（三层）
```python
def retry(max_times=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last = e
            raise last
        return wrapper
    return decorator

@retry(max_times=3)
def call(): ...
```

---

## 附录 B · 一行经典招式

```python
# 字典反转
{v: k for k, v in d.items()}

# 列表去重保序
list(dict.fromkeys(seq))

# 多关键字排序
sorted(users, key=lambda u: (u["age"], -u["salary"]))

# one-hot 编码（NumPy）
np.eye(n_classes)[labels]

# softmax
e = np.exp(x); e / e.sum(axis=1, keepdims=True)

# 标准化
(x - x.mean(axis=0)) / x.std(axis=0)

# 余弦相似度
np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 最大值在二维数组中的位置
np.unravel_index(np.argmax(A), A.shape)

# 字典合并（Python 3.5+）
{**d1, **d2}     # 或 d1 | d2 (Python 3.9+)

# 交换两变量
a, b = b, a
```

---

> **使用建议**：写练习卡住时优先在本文件搜函数名（`Cmd+F`），看到示例再回练习里写。文档随练习推进持续补充。
