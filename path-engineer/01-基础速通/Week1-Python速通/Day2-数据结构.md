# Day 2 · Python 数据结构

> ⏱️ 时间：1.5 小时
> 🎯 目标：掌握 Python 4 大核心数据结构 + Pythonic 招式
> 📋 练习：[`练习/day2_练习.py`](./练习/day2_练习.py)

---

## 0. 心法

> **Python 数据结构比 Java 灵活百倍。**
>
> Java 一个 `ArrayList<Map<String, List<Integer>>>` 写得头大，
> Python 一行 `data = {"a": [1, 2], "b": [3, 4]}` 就完事。

今天学完，你写脚本会非常爽。

---

## 1. 四大核心数据结构（一张表）

| Python | Java 对应 | 可变性 | 有序 | 重复 | 字面量 |
|--------|----------|--------|------|------|--------|
| `list` | `ArrayList` | ✅ 可变 | ✅ 有序 | ✅ 允许 | `[1, 2, 3]` |
| `tuple` | （类似 `record`/不可变 List）| ❌ 不可变 | ✅ 有序 | ✅ 允许 | `(1, 2, 3)` |
| `dict` | `HashMap` | ✅ 可变 | ✅ 有序*| key 不重复 | `{"a": 1}` |
| `set` | `HashSet` | ✅ 可变 | ❌ 无序 | ❌ 不重复 | `{1, 2, 3}` |

> *Python 3.7+ 的 `dict` 保证插入顺序

---

## 2. List（列表）—— 最常用（30 分钟）

### 创建

```python
nums = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]      # 不同类型也行（Java 不行）
empty = []
matrix = [[1, 2], [3, 4]]              # 嵌套
```

### 基础操作

```python
nums = [1, 2, 3, 4, 5]

# 长度
len(nums)              # 5

# 访问（支持负索引！）
nums[0]                # 1（第一个）
nums[-1]               # 5（最后一个）⭐
nums[-2]               # 4（倒数第二个）

# 修改
nums[0] = 100          # nums = [100, 2, 3, 4, 5]

# 添加
nums.append(6)         # 末尾添加
nums.insert(0, 0)      # 指定位置插入
nums.extend([7, 8])    # 添加多个 = nums + [7, 8]

# 删除
nums.remove(3)         # 删除值为 3 的第一个
del nums[0]            # 按索引删除
nums.pop()             # 弹出最后一个
nums.pop(0)            # 弹出指定位置

# 查找
3 in nums              # True / False（包含检查）
nums.index(3)          # 返回索引
nums.count(3)          # 出现次数

# 排序
nums.sort()            # 原地升序
nums.sort(reverse=True)  # 降序
sorted_nums = sorted(nums)  # 返回新列表（不改原）⭐
nums.reverse()         # 原地反转
```

### 切片（Slicing）⭐⭐⭐ Python 杀手锏

> **重点中的重点**，Java 没有这个特性。

```python
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 语法：list[start:stop:step]  （包含 start，不包含 stop）

nums[2:5]      # [2, 3, 4]      索引 2 到 4
nums[:3]       # [0, 1, 2]      从头到索引 2
nums[7:]       # [7, 8, 9]      从索引 7 到末尾
nums[:]        # 完整复制 ⭐⭐
nums[::2]      # [0, 2, 4, 6, 8]   每 2 个取一个
nums[::-1]     # [9, 8, 7, ..., 0] 反转 ⭐⭐⭐
nums[-3:]      # [7, 8, 9]      最后 3 个

# 切片可以赋值
nums[2:5] = [20, 30, 40]   # 替换索引 2-4
```

> 💡 **PyTorch 代码里 `tensor[:, 0]` 这种切片到处都是**，今天必须吃透。

### 列表推导式（List Comprehension）⭐⭐⭐ 最 Pythonic

> **这是 Python 老兵和新手最大的分水岭。**

```python
# Java 写法
List<Integer> squares = new ArrayList<>();
for (int i = 0; i < 10; i++) {
    squares.add(i * i);
}
```

```python
# Python 老式写法（不推荐）
squares = []
for i in range(10):
    squares.append(i * i)

# Python 推导式 ⭐
squares = [i * i for i in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

#### 推导式的完整语法

```
[表达式 for 变量 in 可迭代对象 if 条件]
```

```python
# 1. 基础：每个元素 * 2
[x * 2 for x in [1, 2, 3]]               # [2, 4, 6]

# 2. 加 if 过滤
[x for x in range(20) if x % 2 == 0]     # 偶数 [0, 2, 4, ..., 18]

# 3. if-else 三元（注意位置不同！）
[x if x > 0 else 0 for x in [-1, 2, -3, 4]]   # [0, 2, 0, 4]

# 4. 嵌套循环（笛卡尔积）
[(x, y) for x in [1, 2] for y in ["a", "b"]]
# [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]

# 5. 处理字符串列表
words = ["hello", "world", "python"]
upper = [w.upper() for w in words]       # ['HELLO', 'WORLD', 'PYTHON']

# 6. 应用：从字典提取
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
names = [u["name"] for u in users]       # ['Alice', 'Bob']
```

> ⭐ **看 PyTorch / NumPy / pandas 代码处处是推导式，今天必须熟练。**

### 实用方法

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

sum(nums)          # 31
min(nums)          # 1
max(nums)          # 9
sum(nums) / len(nums)  # 3.875（平均）

# 自定义排序
words = ["python", "go", "java"]
sorted(words, key=len)               # ['go', 'java', 'python']
sorted(words, key=lambda x: -len(x))  # 按长度降序

# 数字列表的常用操作
sorted([3, 1, 4, 1, 5], reverse=True)  # [5, 4, 3, 1, 1]
```

---

## 3. Dict（字典）—— 第二常用（25 分钟）

### 创建

```python
# 字面量
user = {"name": "Alice", "age": 30, "is_admin": False}

# 用 dict()
user = dict(name="Alice", age=30)

# 空字典
empty = {}        # 注意：{} 是空字典，不是空集合
```

### 基础操作

```python
user = {"name": "Alice", "age": 30}

# 访问
user["name"]              # "Alice"
user["height"]            # KeyError ❌

# 安全访问 ⭐
user.get("height")        # None（不会报错）
user.get("height", 1.7)   # 1.7（默认值）

# 添加 / 修改
user["email"] = "a@b.com"  # 添加
user["age"] = 31           # 修改

# 删除
del user["age"]
user.pop("age", None)      # 安全删除（不存在返回 None）

# 检查 key
"name" in user             # True
"phone" not in user        # True

# 长度
len(user)
```

### 遍历（重点）

```python
user = {"name": "Alice", "age": 30, "email": "a@b.com"}

# 1. 只遍历 key
for key in user:
    print(key)
# 等价于
for key in user.keys():
    print(key)

# 2. 只遍历 value
for value in user.values():
    print(value)

# 3. 同时遍历 key 和 value ⭐⭐⭐
for key, value in user.items():
    print(f"{key} = {value}")
```

### 字典推导式 ⭐

```python
# 反转字典（key/value 互换）
original = {"a": 1, "b": 2, "c": 3}
reversed_dict = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}

# 过滤
scores = {"Alice": 85, "Bob": 60, "Charlie": 90}
high_scores = {name: score for name, score in scores.items() if score >= 80}
# {'Alice': 85, 'Charlie': 90}

# 从两个列表创建字典
keys = ["a", "b", "c"]
values = [1, 2, 3]
d = dict(zip(keys, values))           # {'a': 1, 'b': 2, 'c': 3}
d = {k: v for k, v in zip(keys, values)}  # 同上
```

### 实用：collections 模块

```python
from collections import defaultdict, Counter

# defaultdict：访问不存在的 key 时返回默认值，不报错
d = defaultdict(list)
d["fruits"].append("apple")           # 不需要先初始化
d["fruits"].append("banana")
print(d)  # defaultdict(<class 'list'>, {'fruits': ['apple', 'banana']})

# Counter：自动计数 ⭐
words = "the quick brown fox jumps over the lazy dog the".split()
counter = Counter(words)
print(counter)
# Counter({'the': 3, 'quick': 1, 'brown': 1, ...})

print(counter.most_common(3))   # [('the', 3), ('quick', 1), ('brown', 1)]
```

---

## 4. Tuple（元组）—— 不可变 List（10 分钟）

### 创建与使用

```python
# 元组：圆括号或不加括号
point = (3, 5)
point = 3, 5            # 也行（更地道）

# 单元素元组（必须加逗号）
single = (5,)           # ✅ 元组
not_tuple = (5)         # ❌ 这是数字 5

# 访问（和 list 一样）
point[0]                # 3

# 不能修改 ⭐
# point[0] = 10         # TypeError!
```

### Tuple 的核心用途

#### 1. 多返回值（最常见）

```python
def get_min_max(nums):
    return min(nums), max(nums)        # 返回 tuple

low, high = get_min_max([3, 1, 4])     # 解包
```

#### 2. 用作字典 key（list 不行）

```python
locations = {
    (0, 0): "origin",
    (1, 2): "point A",
}
# {[0, 0]: "origin"}  # ❌ list 不能做 key（不可哈希）
```

#### 3. 函数参数解包

```python
def add(a, b):
    return a + b

args = (3, 5)
add(*args)              # = add(3, 5)
```

> 💡 **什么时候用 list，什么时候用 tuple？**
>
> - **list**：内容可能变（用户列表、日志、训练数据 batch）
> - **tuple**：固定结构（坐标、RGB、函数返回多个值）

---

## 5. Set（集合）—— 去重 + 集合运算（10 分钟）

### 创建与使用

```python
# 字面量
s = {1, 2, 3}
empty = set()           # 注意：{} 是空 dict，不是空 set！

# 从 list 创建（去重）⭐
nums = [1, 2, 2, 3, 3, 3]
unique = set(nums)      # {1, 2, 3}
unique_list = list(set(nums))  # [1, 2, 3]

# 操作
s.add(4)
s.remove(1)             # 不存在会报错
s.discard(99)           # 不存在不报错
1 in s                  # True / False
```

### 集合运算（数学课重温）⭐

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b        # 并集 {1, 2, 3, 4, 5, 6}
a & b        # 交集 {3, 4}
a - b        # 差集 {1, 2}
a ^ b        # 对称差 {1, 2, 5, 6}
```

### 实战：用户标签匹配

```python
user_tags = {"python", "java", "ai", "backend"}
job_tags = {"python", "ai", "ml"}

common = user_tags & job_tags   # {'python', 'ai'} 匹配的标签
match_rate = len(common) / len(job_tags)  # 0.67
```

---

## 6. 综合：什么时候用什么？（5 分钟）

| 场景 | 用什么 | 为什么 |
|------|--------|--------|
| 一组顺序数据 | `list` | 可变、有序、最常用 |
| 多个返回值 | `tuple` | 不可变更安全 |
| 键值对 | `dict` | 快速查找 O(1) |
| 去重 / 包含判断 | `set` | 去重 + O(1) 包含查询 |
| 配置 / 函数返回 | `dict` 或 `dataclass` | 自描述 |
| 矩阵数据 | `list` 嵌套 → `numpy.array`（明天学）| 性能 |

---

## 7. 必记的 Pythonic 招式（5 分钟）

### 1. unpacking（解包）

```python
# 列表 / 元组解包
a, b, c = [1, 2, 3]              # a=1, b=2, c=3
first, *rest = [1, 2, 3, 4, 5]   # first=1, rest=[2,3,4,5]
*init, last = [1, 2, 3, 4, 5]    # init=[1,2,3,4], last=5

# 字典解包到函数（看 PyTorch 经常用）
config = {"lr": 0.01, "batch_size": 32}
def train(lr, batch_size):
    print(lr, batch_size)
train(**config)                  # = train(lr=0.01, batch_size=32)

# 列表解包合并
a = [1, 2]
b = [3, 4]
combined = [*a, *b, 5]           # [1, 2, 3, 4, 5]

# 字典解包合并
d1 = {"a": 1}
d2 = {"b": 2}
merged = {**d1, **d2}            # {'a': 1, 'b': 2}
```

### 2. any / all

```python
nums = [1, 2, 3, 4, 5]

any(x > 3 for x in nums)         # True（至少一个）
all(x > 0 for x in nums)         # True（全部）
all(x > 3 for x in nums)         # False
```

### 3. dict.setdefault

```python
counts = {}
for word in ["a", "b", "a", "c", "a"]:
    counts.setdefault(word, 0)
    counts[word] += 1
# 等价更优雅写法：用 Counter
```

---

## 📋 今日任务清单

- [ ] 通读本文档，**手敲**至少 10 段代码
- [ ] 完成 [`练习/day2_练习.py`](./练习/day2_练习.py)
- [ ] 重点掌握：**列表推导式**、**切片**、**dict 遍历**
- [ ] 自测：能不能 30 秒内写出"统计字符串中每个字符出现次数"的代码？

---

## 🎯 自测：今天你应该能...

- [ ] 用列表推导式写一行代码搞定 Java 5 行的活
- [ ] 用切片反转一个 list（`nums[::-1]`）
- [ ] 用 `dict.items()` 同时遍历 key 和 value
- [ ] 用 `set` 做列表去重
- [ ] 看到 `*args` / `**kwargs` 不再懵

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 3 · Python 进阶](./Day3-Python进阶.md)。
