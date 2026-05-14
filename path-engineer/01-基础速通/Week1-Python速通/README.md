# Week 1 · Python 速通（5 天）

> 🎯 **本周目标**：从 Java 老兵 → Python 够用级
>
> ⏱️ **时间预算**：5 天 × 1.5h = 7.5 小时（工作日晚上）+ 周末练习 3h，共约 10h
>
> 🪜 **关键认知**：你不是从 0 学编程，是从 Java 切换到 Python。**重点是"差异点"，不是"语言全貌"。**

---

## 📌 核心心法（先看这个）

### 1. 别想"学完 Python"，目标是"能看懂、能改、能写脚本"

| ✅ 应该做的 | ❌ 不要做的 |
|------------|------------|
| 把 Java 已会的概念在 Python 里找对应 | 看完一整本《Python 编程从入门到精通》 |
| 重点关注 Python 特有的（list comprehension 等）| 用 Python 重写一遍 LeetCode |
| 能看懂别人写的 PyTorch / sklearn 代码 | 学 Django/Flask（你有 Spring）|
| 能写 50 行内的小脚本（数据处理、API 调用）| 学 metaclass / 描述符这些深坑 |

### 2. 学习方式：**对比式学习** + **写代码巩固**

每个知识点的学习套路：

```
1. 看 5 分钟概念
2. 对比 Java 怎么写，Python 怎么写
3. 自己敲一遍代码（不要复制粘贴！）
4. 完成当天的练习题
```

### 3. 心理建设

> **第一天会很别扭**（缩进代替花括号、没分号、动态类型...），
> **第三天就会觉得真香**，
> **第五天看 PyTorch 代码不再怕。**

---

## 🗓️ 5 天规划速览

| 天 | 主题 | 核心内容 | 产出 |
|----|------|---------|------|
| **Day 1** | [基础语法](./Day1-基础语法.md) | 变量、控制流、函数、类 | 把 Java 习惯切到 Python |
| **Day 2** | [数据结构](./Day2-数据结构.md) | list/dict/set/tuple、推导式、切片 | Python 特有招式 |
| **Day 3** | [进阶用法](./Day3-Python进阶.md) | 装饰器、上下文、异常、模块 | 看懂 PyTorch 装饰器 |
| **Day 4** | [NumPy 基础](./Day4-NumPy基础.md) | ndarray、广播、矩阵运算 | 理解 AI 数据结构 |
| **Day 5** | [综合演练](./Day5-综合演练.md) | 读懂代码 + 写小脚本 | 验证学习成果 |

---

## 📦 配套资源

### 必备工具

| 工具 | 用途 | 安装 |
|------|------|------|
| **Python 3.11+** | 语言本体（你已装）| `python3 --version` |
| **Jupyter Lab** | 交互式练习（推荐）| 已装，跑 `bash start_jupyter.sh` |
| **VS Code / PyCharm** | 代码编辑器 | 任选 |

### 推荐资源（精选，按需选 1）

| 资源 | 形式 | 时长 | 推荐度 |
|------|------|------|------|
| [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400) | 文字 | 速读前 30% | ⭐⭐⭐⭐⭐（中文首选）|
| [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/) | 文字 | 1-2h | ⭐⭐⭐⭐ |
| [Real Python](https://realpython.com/) | 文字 | 按需 | ⭐⭐⭐⭐⭐（英文最佳）|
| [Andy Sterland - Python for Java Devs](https://www.youtube.com/results?search_query=python+for+java+developers) | 视频 | 1-2h | ⭐⭐⭐⭐（针对你）|
| 《Fluent Python》 | 书 | 1 个月 | ⭐⭐⭐（学完想深入再看）|

> 💡 **本周策略**：以**本目录的 Day1~5 教程**为主，遇到不懂的查廖雪峰。**别追求看完一整本书。**

### 练习平台（可选）

- [Codewars](https://www.codewars.com/) - 难度递进的小题
- [Exercism Python Track](https://exercism.org/tracks/python) - 有导师审阅
- [LeetCode](https://leetcode.cn) - **不推荐**（不是学语言的方式）

---

## 🎯 本周完成标准（自测）

学完这 5 天，你应该能做到：

- [ ] **看到一段 Python 代码，能猜出大概在做什么**
  - 测试：随机打开一个 `.py` 文件，能读懂 80%
- [ ] **能写一个 50 行的小脚本**
  - 测试：写个脚本读 CSV、过滤数据、保存结果
- [ ] **看到 PyTorch 模型代码不再陌生**
  - 测试：看 `class Net(nn.Module): def __init__(self):` 知道在干嘛
- [ ] **会用 NumPy 做基础矩阵运算**
  - 测试：`np.array([[1,2],[3,4]]) @ np.array([[5,6],[7,8]])` 能心算结果维度
- [ ] **能装饰函数**（`@decorator`）
  - 测试：写一个 `@timer` 装饰器测量函数耗时

---

## 🚀 开始学习

### 推荐节奏

```
工作日晚上（每天 1.5h）：
  20:00 - 20:15  快速浏览当天 Day{N}.md
  20:15 - 21:15  对照教程敲一遍代码
  21:15 - 21:30  做当天练习题（练习/dayN_练习.py）

周末（额外 3h）：
  - 复盘前 5 天的练习
  - 找一段开源 Python 代码读 30 分钟
  - 写一个自己的小脚本（任意主题）
```

### 第一步

👉 现在打开 [Day 1 · 基础语法](./Day1-基础语法.md) 开始学习。

---

## 🆘 卡住了怎么办？

### 通用情况

| 情况 | 解决方式 |
|------|---------|
| 语法不懂 | Google "python xxx 教程" / 问 AI 助手 |
| 跑不通 | 看错误信息（Python 报错很友好），搜错误关键字 |
| 概念混乱 | 回到 Day{N} 教程对照"Java vs Python"小节 |
| 学不下去 | 跳过这一节，继续往后，**别卡住** |

### 📚 专题速查（卡住时直接看）

| 卡住的地方 | 看这里 |
|-----------|------|
| Day 4 NumPy 题 7-9（softmax/one-hot/KNN）| ⭐ [day4_练习_精讲答案.md](./练习/day4_练习_精讲答案.md) |
| `axis=0/1` / `keepdims` / 广播报错 | [Day4 §6.5 卡点专题](./Day4-NumPy基础.md#65-卡点专题4-个最容易迷的-api-) |
| NumPy 任何疑惑（跨教程速查）| [99-资源库/NumPy常见疑惑.md](../../../99-资源库/NumPy常见疑惑.md) |
| Notebook 环境问题 | [99-资源库/Jupyter与Conda环境搭建.md](../../../99-资源库/Jupyter与Conda环境搭建.md) |

---

## 🔗 相关链接

- [阶段 1 总览](../README.md)
- [Week 2 · 经典 ML 扫盲](../Week2-经典ML扫盲/) （下周）
- [path-engineer 主路径](../../README.md)
