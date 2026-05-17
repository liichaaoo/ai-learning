# Week 2 · Transformer（5 天）⭐ 整个阶段的核心

> 🎯 **本周目标**：闭着眼能画 Transformer 架构图，每一块都讲得出"为什么要有它"
>
> ⏱️ **时间预算**：5 天 × 1.5h = 7.5 小时（工作日晚上）+ 周末复盘 2h，共约 9.5h
>
> 🏆 **本周地位**：**整个阶段最重要的一周**——LLM、RAG、Agent、微调、推理优化全部建立在 Transformer 之上

---

## 📌 心法（先看这个）

### 1. 这周到底学到什么程度

| ✅ 应该达到的 | ❌ 不要追求的 |
|------------|------------|
| 看到 Transformer 架构图能指着每一块讲清楚 | 从零实现完整 Transformer 论文版 |
| 能用白话讲 Q / K / V 各自在干什么 | 手推 Attention 反向传播梯度 |
| 知道 Multi-Head 为什么要"多头" | 手算 64 头并行的张量形状 |
| 能说清楚 GPT / BERT / Llama 三者的区别 | 把每个模型的 config 背下来 |
| 知道 Llama 用了 RoPE / RMSNorm / SwiGLU | 推导 RoPE 的复数旋转公式 |

### 2. 学习方式：**先看图 → 再读公式 → 最后看代码**

每个知识点的套路：

```
1. 5 分钟看图建直觉（Jay Alammar 图解最好）
2. 5 分钟看公式（只看核心那一两条）
3. 10 分钟看 PyTorch 实现（看清形状变化）
4. 自己讲一遍给"假想中的产品经理"听
5. 完成当天练习
```

### 3. 心理建设

> **第一天会觉得"Q/K/V 是什么鬼"** —— 正常，看完 Day 2 公式 + Day 3 多头并行就会通。
>
> **第三天**你会发现：**Self-Attention 的核心计算就是 `softmax(QK^T/√d) V` 这一行**。
>
> **第五天**你能在一张白纸上画出 Transformer 完整架构图，并讲清楚 GPT / BERT / Llama 三者的取舍——那一刻你已经"看懂 LLM"了。

---

## 🪜 学习起点

完成 Week 1 后你已经具备的：

- ✅ PyTorch 训练循环（forward → loss → backward → step）—— [Week 1 Day 5](../Week1-神经网络与PyTorch/Day5-训练循环速查.md)
- ✅ `nn.Module` / `nn.Linear` / `nn.LayerNorm` 等基础模块 —— [Week 1 Day 2-3](../Week1-神经网络与PyTorch/)
- ✅ **手搓过 Mini-Attention**（点积 + softmax）—— [阶段 1 · Week 3 Day 5](../../01-基础速通/Week3-数学补盲/Day5-综合应用.md)

> 💡 这意味着：本周不是"从零学 Attention"，而是**把 Mini-Attention 放进 Transformer 整体里去看**——你会发现整个 Transformer 就是 Attention + FFN + 残差 + LayerNorm 的反复堆叠。

---

## 🗓️ 5 天规划速览

| 天 | 主题 | 核心内容 | 产出 |
|----|------|---------|------|
| **Day 1** | [Attention 直观理解](./Day1-Attention直观理解.md) | RNN 的痛 / "看上下文"是什么 / Attention 解决了什么 | 一句话回答"为什么需要 Attention" |
| **Day 2** | [Self-Attention 公式](./Day2-SelfAttention公式.md) ⭐ | Q / K / V 三件套 / 缩放点积 / 因果掩码 | 默写 `softmax(QK^T/√d)V` 并讲清每一步 |
| **Day 3** | [Multi-Head Attention](./Day3-MultiHead多头注意力.md) | 为什么多头 / 张量形状 / 并行计算 | 看到代码能说出每个维度含义 |
| **Day 4** | [Transformer 完整架构](./Day4-Transformer完整架构.md) ⭐ | Encoder / Decoder / Position Embedding / LayerNorm + Residual / FFN | **手画一张完整架构图** |
| **Day 5** | [GPT vs BERT vs Llama](./Day5-三大流派对比.md) | 三大流派的设计选择 + Llama 现代化三件套（RoPE / RMSNorm / SwiGLU）| 一张三模型对比表 |

---

## 🎯 一图速记：本周要刻进脑子的两张图

### 图 1：Self-Attention 一行公式

```
    Attention(Q, K, V) = softmax( QK^T / √d_k ) · V
                               ↑          ↑       ↑
                          相似度矩阵    防梯度爆炸  加权求和
```

### 图 2：Transformer Block（重复堆 N 层就是整个模型）

```
                  ┌─────────────────────────────┐
   x ──────┐      │                             │
           │      │   ┌───────────────────┐     │
           ├──→  +├──→│ Multi-Head Attn   │──┐  │
           │      │   └───────────────────┘  │  │
           │      │                          ↓  │
           │      │     LayerNorm（残差后）  │  │
           │      │            ↓             │  │
           ├─────→│   ┌───────────────────┐  │  │
           │      │   │   FFN (MLP)       │←─┘  │
           │      │   └───────────────────┘     │
           │      │            ↓                │
           └─────→│     LayerNorm               │
                  │            ↓                │
                  │            y                │
                  └─────────────────────────────┘
                     × N 层（GPT-3 是 96 层）
```

> 💡 **本周通关标准**：能闭着眼把这两张图画在白板上，并解释每一个箭头。

---

## 📦 配套资源

### 必备工具

| 工具 | 用途 | 状态 |
|------|------|------|
| **Python + PyTorch** | 看代码、跑 Demo | Week 1 已装 |
| **Jupyter Lab** | 交互式调试张量形状 | Week 1 已装 |
| **画图工具** | 自己画 Transformer 架构图（任选）| 推荐 [excalidraw.com](https://excalidraw.com) |

### 推荐资源（**精挑，按必要性排序**）

| 资源 | 形式 | 时长 | 推荐度 |
|------|------|------|------|
| 🥇 [Jay Alammar - The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/) | 图文 | 30 min | ⭐⭐⭐⭐⭐（**必读 2 遍，全网最佳图解**）|
| 🥇 [Jay Alammar - The Illustrated GPT-2](http://jalammar.github.io/illustrated-gpt2/) | 图文 | 30 min | ⭐⭐⭐⭐⭐（**Day 5 必读**）|
| 🥈 [Andrej Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) | 视频 | 看前 30 min | ⭐⭐⭐⭐⭐（建议看带中文字幕版）|
| 🥈 [李沐《动手学深度学习》第 10/11 章](https://zh.d2l.ai/chapter_attention-mechanisms/index.html) | 文字 | 1.5h | ⭐⭐⭐⭐（中文最佳，配合 Day 2-4）|
| 🥉 [Attention Is All You Need](https://arxiv.org/abs/1706.03762) 论文 | PDF | 只看图 1+图 2 | ⭐⭐⭐（看图就够，公式部分知道在哪即可）|
| 选看 [3Blue1Brown · Attention 可视化](https://www.bilibili.com/video/BV13z421U7cs/) | 视频 | 25 min | ⭐⭐⭐⭐（B 站中文，建立直觉）|

> 💡 **本周策略**：以**本目录的 Day 1~5 教程**为主线，**Jay Alammar 必读两篇**，Karpathy 视频选看前 30 分钟。**别想着把所有资源刷完。**

---

## 🎯 本周完成标准（自测清单）

学完这 5 天，你应该能做到：

- [ ] **白纸画 Transformer 架构图**：能画出 Encoder + Decoder + 残差 + LayerNorm + FFN
- [ ] **白话 + 公式两种方式解释 Attention**：Q / K / V 各自在干什么
- [ ] **解释为什么除以 √d_k**：防止 softmax 进入梯度极小区
- [ ] **解释 Multi-Head 的好处**：让模型同时关注多种关系
- [ ] **解释因果掩码（Causal Mask）**：GPT 为什么"只能看左边"
- [ ] **三大流派对比**：GPT / BERT / Llama 的结构、训练目标、典型用途
- [ ] **Llama 现代化三件套**：RoPE / RMSNorm / SwiGLU 各自解决什么问题（一句话级即可）
- [ ] **不被 Transformer 代码吓到**：阶段 3 看 HuggingFace 模型结构时心里有底

---

## 🚀 开始学习

### 推荐节奏

```
工作日晚上（每天 1.5h）：
  20:00 - 20:20  快速浏览当天 Day{N}.md 全文
  20:20 - 21:00  对照图解资源 + 教程画图、看代码
  21:00 - 21:30  做当天练习题（练习/dayN_*.py）

周末（额外 2h）：
  - 把 Day 4 的架构图自己**重画一遍**（不许抄），讲给"假想产品经理"听
  - 做 Day 5 综合练习：把一个 Transformer Block 跑通
  - 把 GPT/BERT/Llama 对比表整理进笔记
```

### 第一步

👉 现在打开 [Day 1 · Attention 直观理解](./Day1-Attention直观理解.md) 开始学习。

---

## 🆘 卡住了怎么办？

| 情况 | 解决方式 |
|------|---------|
| Q/K/V 概念混乱 | 跳到 Day 2 的"图书馆类比"看一遍，再回来 |
| 张量形状追不过来 | 全程用 `print(x.shape)` 打印，一步步对 |
| `softmax(QK^T/√d_k)V` 推不顺 | Day 2 §3 有逐步分解，照着算一遍数字 |
| 看不懂 Position Embedding | 知道"给每个位置加一个固定的标记向量"就够了，细节交给 Day 4 |
| 觉得 Transformer 太复杂 | **它就是 Attention + FFN + 残差 + LayerNorm 的堆叠**，没第二种东西 |
| 反复纠结 Encoder vs Decoder | 记住：**BERT 只有 Encoder，GPT/Llama 只有 Decoder**——现代 LLM 几乎都是 Decoder-only |

---

## 🧭 本周与后续阶段的衔接

学完本周后，下面的概念你都能丝滑承接：

| 后续话题 | 本周哪里建立的认知 |
|---------|------------------|
| Embedding 向量检索（阶段 3 RAG）| Day 1-2：Attention 中相似度计算就是点积 |
| 上下文窗口（Context Window）| Day 4：Position Embedding + Attention 复杂度 O(n²) |
| KV Cache（推理优化）| Day 3：Multi-Head 中 K/V 是可以缓存的 |
| LoRA 微调（阶段 5）| Day 4：FFN / Attention 的 W 矩阵就是被低秩分解的对象 |
| 选模型（GPT/Llama/Qwen）| Day 5：知道架构差异和适用场景 |

---

## 🔗 相关链接

- ⬆️ [回到阶段 2 总览](../README.md)
- ⬅️ [Week 1 · 神经网络与 PyTorch](../Week1-神经网络与PyTorch/README.md)
- ➡️ [Week 3 · HuggingFace + LLM 推理原理](../Week3-HuggingFace与推理/README.md) （下周）
- 📋 [path-engineer 主路径](../../README.md)
- 🎓 [path-research · Transformer 深入版（可选）](../../../path-research/README.md)
