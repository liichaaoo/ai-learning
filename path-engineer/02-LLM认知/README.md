# 阶段 2 · LLM 认知（3 周）

> 🎯 **目标**：知道 LLM 是怎么工作的——能画框架图、能讲原理、能给团队做 30 分钟分享
>
> ⏱️ **周期**：3 周（约 30 ~ 40 小时）
>
> 🧭 **权重**：⭐⭐⭐（工程师必备的技术认知，但不深究）
>
> 📍 **位置**：6 阶段路线图的第 2 站，承接 [阶段 1 · 基础速通](../01-基础速通/README.md)，为 [阶段 3 · Spring AI 与 RAG](../03-SpringAI与RAG/README.md) 打认知地基

---

## 📌 核心原则

> **理解，不要实现。看图，不要手推。**

- ✅ **要做**：看到 Transformer 架构图，能指着每一块讲清楚它在干什么、为什么这样设计
- ❌ **不做**：从零写 Transformer、手推反向传播梯度、复现论文实验

> 🧭 **判断标准**：能向产品经理用白话讲明白「为什么 ChatGPT 会接话」，比能写出 Self-Attention 的代码更重要。

---

## 🪜 学习起点（你已经具备的）

完成阶段 1 后，你应该已经：

- ✅ Python 能看懂、能写脚本（[阶段 1 · Week 1](../01-基础速通/Week1-Python速通/)）
- ✅ 知道什么是 Embedding、什么是 Softmax（[阶段 1 · Week 3 Day 3](../01-基础速通/Week3-数学补盲/Day3-概率与信息论.md)）
- ✅ **手搓过 Mini-Attention**（[阶段 1 · Week 3 Day 5](../01-基础速通/Week3-数学补盲/Day5-综合应用.md)）

> 💡 这意味着：本阶段不是「从零学 Attention」，而是**站在已有的代码基础上，把它放到 Transformer 整体里去看**。

---

## 🗓️ 3 周计划速览

| 周 | 主题 | 状态 | 核心产出 |
|----|------|------|---------|
| **Week 1** | [神经网络 + PyTorch 速览](./Week1-神经网络与PyTorch/) | ✅ 已开放 | 跑通 MNIST + 永久训练脚手架 |
| **Week 2** | [Transformer（重点）⭐](./Week2-Transformer/) | ✅ 已开放 | **手画 Transformer 架构图** |
| **Week 3** | [HuggingFace + LLM 推理原理](./Week3-HuggingFace与推理/) | ✅ 已开放 | 本地跑通一个开源小模型 |

> 📂 **目录结构**：与阶段 1 保持一致——每周一个子目录，内含 `README.md` + 5 篇 Day 教程 + `练习/` 目录。

---

## 📅 Week 1：神经网络 + PyTorch 速览

> 🎯 **目标**：理解神经网络训练是怎么回事，PyTorch 代码不再是天书。
>
> 📂 **入口**：[`Week1-神经网络与PyTorch/README.md`](./Week1-神经网络与PyTorch/README.md) ✅ 已开放

| 天 | 主题 | 教程 | 练习 |
|----|------|------|------|
| Day 1 | 神经网络基础（神经元/激活/MLP/Loss）| [📖](./Week1-神经网络与PyTorch/Day1-神经网络基础.md) | [📝](./Week1-神经网络与PyTorch/练习/day1_练习.py) |
| Day 2 | PyTorch 入门（上）：Tensor + autograd + nn.Module | [📖](./Week1-神经网络与PyTorch/Day2-PyTorch入门上.md) | [📝](./Week1-神经网络与PyTorch/练习/day2_练习.py) |
| Day 3 | PyTorch 入门（下）：Optimizer + DataLoader + GPU | [📖](./Week1-神经网络与PyTorch/Day3-PyTorch入门下.md) | [📝](./Week1-神经网络与PyTorch/练习/day3_练习.py) |
| Day 4 | MNIST 实战 ⭐ | [📖](./Week1-神经网络与PyTorch/Day4-MNIST实战.md) | [📝](./Week1-神经网络与PyTorch/练习/day4_mnist.py) |
| Day 5 | 训练循环模板速查 + 综合演练 | [📖](./Week1-神经网络与PyTorch/Day5-训练循环速查.md) | [📝](./Week1-神经网络与PyTorch/练习/day5_综合.py) |

### 🔑 必须建立的认知（不需要会推导）

- **反向传播**：知道它是「自动求梯度」即可，PyTorch `loss.backward()` 一行搞定
- **梯度下降**：参数 = 参数 - 学习率 × 梯度，就这一个公式
- **Loss**：模型预测和真实答案的"距离"，越小越好

### 📚 推荐资源

- [PyTorch 官方 60 分钟入门](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html)（**必跑**）
- [李宏毅深度学习课程](https://www.bilibili.com/video/BV1Wv411h7kN/)（B 站，前 5 节）
- [3Blue1Brown - 神经网络系列](https://www.bilibili.com/video/BV1bx411M7Zx/)（直观理解，强烈推荐）

---

## 📅 Week 2：Transformer（最重要的一周）⭐

> 🎯 **目标**：闭着眼能画 Transformer 架构图，并且每一块都能讲出「为什么要有它」。
>
> 📂 **入口**：[`Week2-Transformer/README.md`](./Week2-Transformer/README.md) ✅ 已开放
>
> ⚠️ 这一周是整个阶段的核心。LLM 全部建立在 Transformer 之上，**RAG / Agent / 微调 / 推理优化**全是它的衍生话题。

| 天 | 主题 | 教程 | 练习 |
|----|------|------|------|
| Day 1 | Attention 直观理解（RNN 痛点 + Q/K/V 直觉）| [📖](./Week2-Transformer/Day1-Attention直观理解.md) | [📝](./Week2-Transformer/练习/day1_attention直觉.py) |
| Day 2 | Self-Attention 公式 ⭐（缩放点积 + 因果掩码）| [📖](./Week2-Transformer/Day2-SelfAttention公式.md) | [📝](./Week2-Transformer/练习/day2_自注意力实现.py) |
| Day 3 | Multi-Head Attention（为什么多头 + 张量形状）| [📖](./Week2-Transformer/Day3-MultiHead多头注意力.md) | [📝](./Week2-Transformer/练习/day3_多头注意力.py) |
| Day 4 | Transformer 完整架构 ⭐（PE/LN/Residual/FFN）| [📖](./Week2-Transformer/Day4-Transformer完整架构.md) | [📝](./Week2-Transformer/练习/day4_transformer_block.py) |
| Day 5 | GPT vs BERT vs Llama（现代化三件套）| [📖](./Week2-Transformer/Day5-三大流派对比.md) | [📝](./Week2-Transformer/练习/day5_流派对比与综合.py) |

### 🧠 Day 5 三大架构对比速览

| 模型 | 结构 | 训练目标 | 典型用途 | 关键技术点 |
|------|------|---------|---------|----------|
| **BERT** | Encoder-only | 完形填空（MLM）| 文本理解、分类、检索 | 双向 Attention |
| **GPT** | Decoder-only | 预测下一个词（CLM）| 生成、对话 | 因果掩码（Causal Mask）|
| **Llama** | Decoder-only（增强）| 同 GPT | 开源生态、可微调 | **RoPE + RMSNorm + SwiGLU**（必记三件套）|

> 💡 **记忆口诀**：BERT 看两边，GPT 只往左；Llama 是 GPT 的"现代化装修版"。

### 📚 必看资源（精挑）

- 🥇 [Jay Alammar - The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)（**全网最佳图解，必读 2 遍**）
- 🥈 [Andrej Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)（**前 30 分钟看完即可**）
- 🥉 [Attention Is All You Need 论文](https://arxiv.org/abs/1706.03762)（**只看图 1 + 图 2**）
- 中文：[李沐《动手学深度学习》第 10 章](https://zh.d2l.ai/chapter_attention-mechanisms/index.html)（精读 Attention 部分）

### ❌ 本周明确不做

- 不要从零实现完整 Transformer（不是工程派的赛道）
- 不要手推梯度公式
- 不要纠结于"绝对位置编码 vs 相对位置编码"的数学细节，**知道 Llama 用 RoPE 即可**

---

## 📅 Week 3：HuggingFace + LLM 推理原理

> 🎯 **目标**：能用 HuggingFace 加载并跑通一个开源小模型，理解推理参数对效果的影响。
>
> 📂 **入口**：[`Week3-HuggingFace与推理/README.md`](./Week3-HuggingFace与推理/README.md) ✅ 已开放

| 天 | 主题 | 教程 | 练习 |
|----|------|------|------|
| Day 1 | HuggingFace 三件套（transformers + tokenizers + pipeline）| [📖](./Week3-HuggingFace与推理/Day1-HuggingFace三件套.md) | [📝](./Week3-HuggingFace与推理/练习/day1_pipeline速通.py) |
| Day 2 | LLM 推理参数 ⭐（Temperature / Top-p / Top-k）| [📖](./Week3-HuggingFace与推理/Day2-LLM推理参数.md) | [📝](./Week3-HuggingFace与推理/练习/day2_采样参数实验.py) |
| Day 3 | 训练范式认知级（Pre-train → SFT → RLHF/DPO）| [📖](./Week3-HuggingFace与推理/Day3-训练范式全流程.md) | [📝](./Week3-HuggingFace与推理/练习/day3_训练范式自测.py) |
| Day 4 | 参数高效微调认知级（LoRA / QLoRA / 量化）| [📖](./Week3-HuggingFace与推理/Day4-LoRA与量化.md) | [📝](./Week3-HuggingFace与推理/练习/day4_量化与peft.py) |
| Day 5 | 实战：本地跑通开源模型 ⭐ | [📖](./Week3-HuggingFace与推理/Day5-本地跑通开源模型.md) | [📝](./Week3-HuggingFace与推理/练习/day5_本地对话脚本.py) |

### 🔑 推理参数必须烂熟于心（面试高频）

| 参数 | 作用 | 调高的影响 | 工程默认值 |
|------|------|-----------|-----------|
| **Temperature** | 输出"创造性" | 更随机、更发散 | 0.7（聊天）/ 0.0（事实）|
| **Top-p**（核采样）| 候选词概率累积阈值 | 候选池更大 | 0.9 |
| **Top-k** | 只在 Top-k 个候选词里采样 | 候选池更大 | 40 ~ 50 |
| **max_tokens** | 最大输出长度 | 更长（更慢、更贵）| 按场景设 |
| **Context Window** | 模型一次能"看到"多少 token | — | GPT-4o: 128K，Llama-3: 8K ~ 128K |

> 💡 **工程建议**：RAG 场景 Temperature = 0；创意写作 0.7 ~ 1.0；二选一就用 Top-p（0.9）盖过 Top-k。

### 📚 推荐资源

- [HuggingFace LLM Course](https://huggingface.co/learn/llm-course)（**官方课程，章节 1-3 必看**）
- [Datawhale《大模型基础》](https://github.com/datawhalechina/so-large-lm)（中文，章节 4-5）
- [LoRA 论文图解](https://huggingface.co/docs/peft/conceptual_guides/lora)（10 分钟看懂）

---

## ✅ 阶段完成标准（自检清单）

完成本阶段后，应能做到：

- [ ] 一张白纸 + 一支笔，**手画 Transformer 架构图**并讲清楚每一层
- [ ] 用白话和公式两种方式解释 Attention（Q / K / V 分别是什么）
- [ ] 说清楚 GPT / BERT / Llama 的结构差异和适用场景
- [ ] 用 HuggingFace 在本地跑通一个开源小模型并做过 Prompt 实验
- [ ] 解释清楚 Token / Context Window / Temperature / Top-p 的含义和工程取值
- [ ] 知道 LoRA / 量化 / RLHF **是什么、解决什么问题**（不需要会做）
- [ ] 🎤 **终极测试：能给团队做一次 30 分钟的"LLM 工作原理"分享**

### 🎤 30 分钟分享建议提纲

```
1. (3 min)  开场：从 ChatGPT 一句话回答，倒推它的工作流程
2. (5 min)  Token 化与 Embedding：文字怎么变成向量
3. (8 min)  Transformer 架构：Self-Attention + Multi-Head + 残差
4. (5 min)  GPT 生成机制：自回归 + 采样（Temperature / Top-p）
5. (5 min)  训练全流程：Pre-train → SFT → RLHF
6. (3 min)  作为工程师，我们关心什么：Context / 成本 / 延迟 / 微调
7. (1 min)  Q&A
```

> 💡 **不一定真去分享**，但要写得出讲得出。这是检验是否「真的懂」的最硬标准。

---

## 📝 笔记沉淀清单

本阶段建议在 `02-LLM认知/笔记/` 下沉淀以下笔记（用自己的话写，不要抄）：

- [ ] `Attention机制详解.md`（白话 + 公式 + 自画图）
- [ ] `Transformer架构图.md`（含 Encoder / Decoder / Llama 三版对比）
- [ ] `GPT-BERT-Llama对比.md`（含训练目标、典型应用、关键技术）
- [ ] `LLM推理参数速查.md`（Temperature / Top-p / Top-k 一张表）
- [ ] `HuggingFace使用速查.md`（三件套常用 API + 加载本地模型模板）
- [ ] `LoRA与量化认知卡.md`（一张图说清原理 + 解决什么问题）

> 📌 笔记的标准：**离开 3 个月再回来看，能 5 分钟想起来。**

---

## 🚧 常见误区与避坑

| 误区 | 正确姿势 |
|------|---------|
| 想从零实现 Transformer 才算"懂" | 工程派只需「能讲清楚每一块」就够 |
| 卡在反向传播数学推导 | 跳过，PyTorch 帮你做，知道是"自动求梯度"即可 |
| 试图读完 Karpathy 整个 2 小时视频 | 前 30 分钟就够，超出本阶段权重 |
| 在 Position Embedding 各种变体里钻牛角尖 | 知道 Llama 用 RoPE 就行 |
| 觉得数学不够强、不敢往下学 | **这是错觉**，工程派的优势是产出，不是推导 |

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 3 · Spring AI 与 RAG](../03-SpringAI与RAG/README.md) ⭐ **核心阶段（6 周）**

> 🎯 阶段 3 开始你将有第一个**能写进简历的项目**——企业知识库 RAG 系统。本阶段建立的 Transformer / Embedding / 推理参数认知，会在 RAG 的每一个环节里被反复用到。

---

## 🔗 相关链接

- 📋 [path-engineer 主路径](../README.md)
- ⬅️ [上一阶段：基础速通](../01-基础速通/README.md)
- ➡️ [下一阶段：Spring AI 与 RAG](../03-SpringAI与RAG/README.md)
- 🎓 [path-research（学院派对应章节，可作为深入阅读）](../../path-research/README.md)
- 📊 [岗位技能图谱](../../00-学习总览/AI大模型岗位技能图谱.md)
