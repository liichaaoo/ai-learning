# Day 1 · Python 基础语法（Java 对照版）

> ⏱️ 时间：1.5 小时
> 🎯 目标：把 Java 习惯切到 Python，不再被语法问题卡住
> 📋 练习：[`练习/day1_练习.py`](./练习/day1_练习.py)

---

## 0. 环境快速验证（5 分钟）

打开终端，运行：

```bash
python3 --version
# 应该看到 Python 3.11.x 或更高
```

写个 Hello World：

```bash
python3 -c "print('Hello, Python!')"
```

✅ 输出 `Hello, Python!` 就准备好了。

---

## 1. Java vs Python 一张表概览（10 分钟）

| 维度 | Java | Python |
|------|------|--------|
| 类型 | 静态强类型 | **动态强类型** |
| 编译 | 编译为字节码 | 解释执行（也有字节码缓存）|
| 代码块 | `{ }` 花括号 | **缩进**（4 空格）|
| 语句结尾 | `;` 分号 | 换行（一般不要分号）|
| 变量声明 | `int x = 5;` | `x = 5`（不需要类型） |
| 注释 | `//` 或 `/* */` | `#` 或 `""" """` |
| 字符串 | `"abc"` 双引号 | `'abc'` / `"abc"` 都行 |
| 入口 | `public static void main` | `if __name__ == "__main__":` |
| 包管理 | Maven/Gradle | **pip** + venv/conda |
| 标准库 | JDK | Python Standard Library |

---

## 2. 变量与数据类型（15 分钟）

### Java vs Python 写法对比

```java
// Java
int age = 30;
double salary = 12345.67;
boolean isActive = true;
String name = "fletcher";
```

```python
# Python（动态类型，不需要声明）
age = 30
salary = 12345.67
is_active = True            # 注意：True/False 首字母大写
name = "fletcher"

# 想看类型？
print(type(age))            # <class 'int'>
print(type(salary))         # <class 'float'>
print(type(is_active))      # <class 'bool'>
print(type(name))           # <class 'str'>
```

### 几个关键差异

#### 1. 命名约定：snake_case 而不是 camelCase

```java
// Java
String userName;
int maxRetryCount;
```

```python
# Python（PEP 8 规范）
user_name = "..."           # 变量、函数：snake_case
MAX_RETRY_COUNT = 3         # 常量：UPPER_SNAKE_CASE
class UserService:          # 类名：PascalCase
    pass
```

#### 2. 没有 null，是 None

```java
String x = null;
if (x == null) { ... }
```

```python
x = None
if x is None: ...           # 用 is 不是 ==（推荐）
# if x == None: ... 也能用，但不地道
```

#### 3. 数字没有 `int` / `long` / `double` 之分

Python 的 `int` 自动支持任意大数（不会溢出）：

```python
big = 2 ** 100              # 1267650600228229401496703205376
print(big)                  # 直接能算，不溢出
```

`float` 是双精度，没有 `float`/`double` 区分。

#### 4. 字符串：单引号双引号都行 + f-string

```java
// Java
String greeting = "Hello, " + name + "!";
String s = String.format("Age: %d", age);
```

```python
# Python
greeting = "Hello, " + name + "!"             # 拼接（不推荐）
greeting = f"Hello, {name}!"                  # f-string ⭐ 主流写法
greeting = "Hello, {}!".format(name)          # 老写法
greeting = "Age: %d" % age                    # 更老的写法

# f-string 还能格式化
pi = 3.14159
print(f"{pi:.2f}")                            # 3.14
print(f"{1234567:,}")                         # 1,234,567
```

> 💡 **记住一个就够：用 f-string**

---

## 3. 控制流（15 分钟）

### if / elif / else

```java
// Java
if (x > 0) {
    System.out.println("positive");
} else if (x == 0) {
    System.out.println("zero");
} else {
    System.out.println("negative");
}
```

```python
# Python
if x > 0:                           # 注意冒号
    print("positive")
elif x == 0:                        # elif，不是 else if
    print("zero")
else:
    print("negative")
# 没有花括号，全靠缩进！
```

### for 循环：和 Java 完全不同

Java 的 `for (int i = 0; i < 10; i++)` 在 Python 里写法不同：

```python
# 1. 遍历范围
for i in range(10):                 # 0 到 9
    print(i)

for i in range(1, 11):              # 1 到 10
    print(i)

for i in range(0, 100, 5):          # 0, 5, 10, ... 95（步长 5）
    print(i)

# 2. 遍历集合（Java 的 enhanced for）
names = ["Alice", "Bob", "Charlie"]
for name in names:
    print(name)

# 3. 同时遍历下标和元素：enumerate ⭐
for i, name in enumerate(names):
    print(f"{i}: {name}")
# 输出: 0: Alice  1: Bob  2: Charlie

# 4. 同时遍历两个列表：zip ⭐
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age}")
```

### while 循环

```python
count = 0
while count < 5:
    print(count)
    count += 1                      # 没有 ++ 操作符！

# break / continue 和 Java 一样
```

### 三元表达式

```java
// Java
String result = (x > 0) ? "positive" : "non-positive";
```

```python
# Python（顺序很怪：值 if 条件 else 备选）
result = "positive" if x > 0 else "non-positive"
```

---

## 4. 函数（20 分钟）

### 基础定义

```java
// Java
public int add(int a, int b) {
    return a + b;
}
```

```python
# Python
def add(a, b):                      # 不需要声明返回类型
    return a + b

# 调用
result = add(3, 5)
```

### 类型注解（可选但推荐）

虽然 Python 是动态类型，但**写类型注解能让代码更易读**：

```python
def add(a: int, b: int) -> int:     # 注解只是提示，不会强制检查
    return a + b
```

> 💡 **看 PyTorch / FastAPI 代码经常会看到这种写法，要能看懂**

### 默认参数 ⭐ 比 Java 强大

```python
def greet(name, greeting="Hello"):  # 默认值
    return f"{greeting}, {name}!"

greet("Alice")                      # "Hello, Alice!"
greet("Bob", "Hi")                  # "Hi, Bob!"
greet("Charlie", greeting="Hey")    # "Hey, Charlie!"  关键字参数
```

### 多返回值（用元组）

```python
def divmod_custom(a, b):
    return a // b, a % b            # 返回元组

quotient, remainder = divmod_custom(10, 3)
print(quotient, remainder)          # 3 1
```

> ⚠️ **Java 没有这个特性，Python 老兵的常用招式**

### *args 和 **kwargs（看到 PyTorch 代码必懂）

```python
def my_function(*args, **kwargs):
    print("位置参数:", args)         # tuple
    print("关键字参数:", kwargs)     # dict

my_function(1, 2, 3, name="Alice", age=30)
# 位置参数: (1, 2, 3)
# 关键字参数: {'name': 'Alice', 'age': 30}
```

> 💡 PyTorch 里大量这种写法：`def forward(self, *args, **kwargs)`，看到了不要怕。

---

## 5. 类与对象（25 分钟）

### Java vs Python 类定义对比

```java
// Java
public class User {
    private String name;
    private int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String greet() {
        return "Hi, I'm " + name;
    }
}

User u = new User("Alice", 30);
```

```python
# Python（同样功能）
class User:
    def __init__(self, name, age):       # 构造方法（魔法方法之一）
        self.name = name                  # 没有 this，是 self
        self.age = age

    def greet(self):                      # 实例方法第一个参数永远是 self
        return f"Hi, I'm {self.name}"

u = User("Alice", 30)                     # 没有 new 关键字
print(u.greet())                          # "Hi, I'm Alice"
print(u.name)                             # 直接访问，没有 getter
```

### 几个关键差异

#### 1. 没有 `new` 关键字

```python
u = User("Alice", 30)        # ✅ 直接调用类名
# u = new User("Alice", 30)  # ❌ Java 习惯，Python 不需要
```

#### 2. 没有真正的 private（约定俗成）

```python
class User:
    def __init__(self, name):
        self.name = name              # public
        self._password = "xxx"        # 单下划线 = "约定的"私有（仍可访问，但表示别用）
        self.__secret = "yyy"         # 双下划线 = name mangling（变成 _User__secret）

u = User("Alice")
print(u._password)               # 能访问，但你别用
# print(u.__secret)              # AttributeError，但 print(u._User__secret) 能访问
```

> 💡 Python 哲学："**我们都是负责任的成年人**"，不靠语言强制。

#### 3. 继承

```python
class Admin(User):                    # 继承
    def __init__(self, name, age, role):
        super().__init__(name, age)   # 调父类构造
        self.role = role

    def greet(self):                  # 重写
        return f"Admin {self.name}"
```

#### 4. dataclass（推荐，相当于 Java 的 record / Lombok）

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

u = User("Alice", 30)
print(u)                              # User(name='Alice', age=30) 自动 toString
```

> ⭐ **强烈推荐**：写"纯数据类"用 dataclass，省事。

---

## 6. 模块与导入（10 分钟）

### Java vs Python 对比

```java
// Java
import java.util.List;
import java.util.ArrayList;
import com.example.MyClass;
```

```python
# Python
import math                           # 整个模块
from math import sqrt, pi             # 从模块导入特定符号
from math import *                    # 全部导入（不推荐）
import numpy as np                    # 导入并改名 ⭐ 主流写法

print(math.sqrt(16))                  # 4.0
print(sqrt(16))                       # 4.0
print(np.array([1, 2, 3]))            # PyTorch/numpy 全都这么写
```

### 主程序入口

```python
# my_script.py
def main():
    print("Hello from main")

if __name__ == "__main__":            # 等价于 Java 的 main 方法
    main()
```

> 💡 这一句 `if __name__ == "__main__":` **必须记住**，所有 Python 脚本都用它。

---

## 7. 你必须知道的"Pythonic"小招式（10 分钟）

学了 Java 7 年，这些是 Python 特有的"地道"写法：

### 1. 链式比较

```java
// Java
if (0 < x && x < 100) { ... }
```

```python
# Python
if 0 < x < 100:        # ✅ 直接连写
    ...
```

### 2. 多重赋值 / 解包

```python
a, b = 1, 2                       # 同时赋值
a, b = b, a                       # 交换变量（不需要 temp）
first, *rest = [1, 2, 3, 4]       # first=1, rest=[2,3,4]
```

### 3. in 操作符

```python
if "alice" in ["alice", "bob"]:    # 列表包含
    ...
if "key" in {"key": "value"}:      # 字典是否有 key
    ...
if "py" in "python":               # 字符串包含
    ...
```

### 4. truthy / falsy

```python
# 这些都被认为是 False
if not 0: print("0 is falsy")
if not "": print("空字符串是 falsy")
if not []: print("空列表是 falsy")
if not None: print("None 是 falsy")

# 习惯写法
my_list = []
if my_list:                # 等价于 if len(my_list) > 0
    print("has items")
```

---

## 📋 今日任务清单

完成下面 5 件事就算今天达标：

- [x] 验证 Python 环境能跑（终端 `python3 --version`）
- [x] 通读本文档，对照 Java 找差异点
- [x] 把上面的代码片段**手敲一遍**（不要复制！至少敲 3 段）
- [x] 完成 [`练习/day1_练习.py`](./练习/day1_练习.py)（约 8 道小题）
- [x] 在终端运行 `python3 day1_练习.py` 看输出对不对

---

## 🆘 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| `IndentationError` | 缩进不一致（混了 tab 和空格）| 全用 4 空格 |
| `NameError: name 'xxx' is not defined` | 用了未定义变量 | 检查拼写、检查作用域 |
| `print` 没换行 | Python 默认换行，Java 是 `print` 不换行 | `print(x, end="")` 不换行 |
| `"abc" + 5` 报错 | 字符串不会自动转换数字 | `"abc" + str(5)` |

---

## 🎯 自测：今天你应该能...

- [x] 解释 Python 缩进 vs Java 花括号
- [x] 写一个带默认参数的函数
- [x] 写一个简单的类（含构造方法和实例方法）
- [x] 用 `enumerate` 和 `zip` 遍历集合
- [x] 写一个 f-string 格式化输出

---

## ⏭️ 明天

完成今天的练习后，进入 [Day 2 · 数据结构](./Day2-数据结构.md)。
