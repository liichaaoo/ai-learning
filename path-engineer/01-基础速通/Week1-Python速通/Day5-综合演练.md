# Day 5 · 综合演练

> ⏱️ 时间：1.5 小时
> 🎯 目标：把前 4 天学的揉在一起，写出真实可跑的小项目
> 📋 练习：[`练习/day5_综合项目.py`](./练习/day5_综合项目.py)

---

## 0. 心法

> **学语言的最后一公里不是看书，是写一段你能跑通的代码。**
>
> 今天不是新概念，是**把前 4 天的招式攒一起做一件事**。

---

## 1. 今天做什么

下面三选一（按你兴趣选，**至少做完 1 个**）：

### 项目 A：日志分析工具（推荐入门级）

> 给 Java 老兵的：你天天看的日志，今天用 Python 解析

**功能**：
- 读一个日志文件
- 统计 INFO / WARN / ERROR 各占多少
- 找出报错最频繁的 Top 5 错误
- 生成一份 markdown 报告

**用到的招式**：文件 IO、字符串处理、正则、Counter、推导式

### 项目 B：批量调用 LLM API（最贴你目标）⭐

> 直接对接你未来学的 Spring AI

**功能**：
- 读一个 CSV（包含问题列表）
- 批量调用 OpenAI / 通义 API
- 把答案存到新 CSV
- 加重试 + 限流 + 进度条

**用到的招式**：装饰器（重试）、文件 IO、HTTP 调用、错误处理

### 项目 C：迷你版 KNN 分类器

> 把 Day 4 的 NumPy 用上

**功能**：
- 加载 sklearn 的鸢尾花数据集
- 自己实现 KNN（不用 sklearn 的现成的）
- 评估准确率

**用到的招式**：NumPy 全套、距离计算、广播、argsort

---

## 2. 项目 B 完整教学（推荐做这个）

下面以**项目 B（批量调用 LLM API）**为例，详细教你怎么做。其他两个套路类似。

### 准备：申请一个免费 API Key

#### 推荐方案：通义千问（阿里云，国内首选）

1. 打开 https://dashscope.aliyun.com/
2. 用阿里云账号登录（没有就注册）
3. 进 "API-KEY 管理" 创建一个 key
4. **新用户有大量免费额度**（够你练手 100 次以上）

#### 或者：OpenAI（要科学上网 + 信用卡）

```bash
# 把 key 设为环境变量（保护隐私，不要写代码里）
export DASHSCOPE_API_KEY="sk-xxx"
# 或加到 ~/.zshrc 永久生效
```

### 装依赖

```bash
pip install openai pandas tqdm
```

> 通义千问兼容 OpenAI 协议，所以用 `openai` 包就行。

### 第 1 版：单次调用（5 分钟搞通）

```python
"""
最简单：调一次 LLM
"""
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义千问的地址
)

response = client.chat.completions.create(
    model="qwen-turbo",                    # 通义千问 turbo（便宜版）
    messages=[
        {"role": "system", "content": "你是一个简洁的 AI 助手"},
        {"role": "user", "content": "用 30 字介绍 Python"},
    ],
)

print(response.choices[0].message.content)
```

跑一下，看到 LLM 给你回的话，你就**第一次成功调用了大模型**。 🎉

### 第 2 版：加上类型注解 + 错误处理

```python
import os
from typing import Optional
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def ask_llm(question: str, system_prompt: str = "你是一个 AI 助手") -> Optional[str]:
    """
    调用 LLM，返回回答内容。失败时返回 None。

    :param question: 用户问题
    :param system_prompt: 系统提示词
    :return: LLM 的回答 / None
    """
    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"调用失败: {e}")
        return None


# 使用
answer = ask_llm("用一句话总结你自己")
print(answer)
```

### 第 3 版：加重试装饰器（用 Day 3 学的）⭐

```python
import time
from functools import wraps


def retry(max_times: int = 3, delay: float = 1.0):
    """重试装饰器：异常时自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"第 {attempt}/{max_times} 次失败: {e}")
                    if attempt < max_times:
                        time.sleep(delay * attempt)  # 指数退避
            raise last_error
        return wrapper
    return decorator


@retry(max_times=3, delay=1.0)
def ask_llm_with_retry(question: str) -> str:
    response = client.chat.completions.create(
        model="qwen-turbo",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content
```

### 第 4 版：批量处理 + 进度条

```python
import pandas as pd
from tqdm import tqdm

# 准备问题（也可从 CSV 读）
questions = [
    "什么是机器学习？",
    "Python 和 Java 的区别？",
    "什么是 RAG？",
    "什么是 Transformer？",
    "向量数据库有哪些？",
]

# 批量调用，带进度条 ⭐
results = []
for q in tqdm(questions, desc="调用 LLM"):
    answer = ask_llm_with_retry(q)
    results.append({"question": q, "answer": answer})

# 保存到 CSV
df = pd.DataFrame(results)
df.to_csv("llm_answers.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ 完成，已保存到 llm_answers.csv")
```

### 第 5 版：完整版（限流 + 上下文管理 + 日志）

完整代码在 [`练习/day5_综合项目.py`](./练习/day5_综合项目.py)，已经帮你打好骨架。

---

## 3. 推荐做的练习路径

```
1. 跟着上面 5 步，把项目 B 跑通（约 1h）
   ↓
2. 改一个 system_prompt，让 LLM 回答风格变化
   ↓
3. 把问题列表换成你真正想问的（如：写代码用、学习问题）
   ↓
4. 把答案存成 markdown 而不是 CSV（更易读）
   ↓
5. 给项目加 README，git commit
```

---

## 4. 学完今天的标志

学完 Week 1，你应该能：

- [ ] **没有 Python 恐惧**：看到 .py 文件不再头大
- [ ] **能写小工具脚本**：50-200 行的项目能独立完成
- [ ] **能看 PyTorch / FastAPI / Spring AI Python 客户端代码**：基本能读懂
- [ ] **能调用 LLM API**：这是阶段 3 的预热
- [ ] **NumPy 基础矩阵运算**：会切片、矩阵乘、broadcasting

---

## 5. 一个小检验

你应该能 30 秒内写出下面的代码（不查资料）：

```python
import numpy as np

# 1. 创建一个 (10, 5) 的矩阵，每行减去自己的均值
data = np.random.randn(10, 5)
data_centered = data - data.mean(axis=1, keepdims=True)

# 2. 把一个 dict 列表转成姓名列表
users = [{"name": "A"}, {"name": "B"}]
names = [u["name"] for u in users]

# 3. 装饰器测时间
import time
from functools import wraps

def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.time() - start:.2f}s")
        return result
    return wrapper

@timing
def my_func():
    time.sleep(0.5)
my_func()
```

如果**全部能写出来**，Week 1 完美通关。

---

## 📋 今日任务清单

- [ ] 选一个项目（A / B / C），看完对应教学
- [ ] 跟着第 1-5 版**逐步**跑通，不要直接跳到完整版
- [ ] 完成 [`练习/day5_综合项目.py`](./练习/day5_综合项目.py)
- [ ] 把代码 git commit
- [ ] 在周报里写下"我做了 XXX"

---

## 🎯 自测：Week 1 你应该全部能...

- [ ] 写一个 100 行内的 Python 项目（功能完整）
- [ ] 看 PyTorch / Spring AI Python 客户端代码不慌
- [ ] 用 NumPy 做矩阵运算
- [ ] 自己写装饰器
- [ ] 调用一次 LLM API ⭐⭐⭐
- [ ] **不再被"Python 不熟"焦虑**

---

## 🎉 完成 Week 1，干得漂亮

下周（Week 2）进入：经典 ML 扫盲 + 用 path-research 里你已有的 Notebook 复习

参考：[`Week2-经典ML扫盲/`](../Week2-经典ML扫盲/)（下周开放）

---

## 🔗 相关链接

- [Week 1 总览](./README.md)
- [回到阶段 1 总览](../README.md)
- [path-engineer 主路径](../../README.md)
