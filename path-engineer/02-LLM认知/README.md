# 阶段 2 · LLM 认知（3 周）

> 🎯 **目标**：知道 LLM 是怎么工作的，能画框架图、能讲原理
>
> ⏱️ **周期**：3 周
>
> 🧭 **权重**：⭐⭐⭐（工程师必备的技术认知，但不深究）

---

## 📌 核心原则

> **理解，不要实现。**
>
> 你不需要从零写一个 Transformer，
> 但你需要看到 Transformer 时**知道每一块在干什么**。

---

## 🗓️ 3 周计划

### Week 1：神经网络 + PyTorch 速览

- [ ] **Day 1**：神经网络基础概念
  - 神经元、激活函数（Sigmoid/ReLU/GeLU）
  - MLP（多层感知机）
  - 前向传播、损失函数
  - **认知反向传播**（不手推）

- [ ] **Day 2-3**：PyTorch 入门
  - `nn.Module`：模型定义
  - `optimizer`：优化器（SGD、Adam）
  - `DataLoader`：数据加载
  - GPU 调用（`.to('cuda')`）

- [ ] **Day 4-5**：实战
  - 跑通 MNIST 手写识别（30 行代码）
  - 理解一个完整训练循环：
    ```
    for epoch:
      for batch:
        forward → loss → backward → step
    ```

#### 📚 推荐资源
- [PyTorch 官方 60 分钟入门](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html)
- B 站李宏毅深度学习课程（前 5 节）

---

### Week 2：Transformer（重点但不深究）

> ⭐ **本阶段最重要的一周**。LLM 全部建立在 Transformer 之上。

- [ ] **Day 1-2**：Attention 机制
  - 直观理解：让模型"看上下文"
  - Self-Attention 计算公式
  - 为什么是 Q / K / V

- [ ] **Day 3**：Multi-Head Attention
  - 为什么要多头
  - 多头怎么并行

- [ ] **Day 4**：Transformer 完整架构
  - Encoder vs Decoder
  - Position Embedding（绝对/相对/RoPE）
  - LayerNorm + Residual
  - **能画出架构图**

- [ ] **Day 5**：GPT vs BERT vs Llama
  - GPT：Decoder-only
  - BERT：Encoder-only
  - Llama：Decoder-only + RoPE + RMSNorm + SwiGLU

#### 📚 必看资源
- [Jay Alammar - The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)（必读）
- [Andrej Karpathy - Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)（重点看前 30 分钟）
- 论文：《Attention Is All You Need》（看图就行）

#### ❌ 不做
- 不要从零实现 Transformer（不是你的赛道）
- 不要手推梯度

---

### Week 3：HuggingFace + LLM 基础原理

- [ ] **Day 1**：HuggingFace 三件套
  - `transformers`：模型加载
  - `tokenizers`：分词器
  - `datasets`：数据集
  - 跑通 `pipeline()` 做文本任务

- [ ] **Day 2**：LLM 推理参数
  - **Token 与 Context Window**
  - Temperature（创造性）
  - Top-p / Top-k（采样策略）
  - max_tokens

- [ ] **Day 3**：训练范式（概念级）
  - 预训练（Pre-training）
  - SFT（有监督微调）
  - RLHF / DPO（对齐）
  - **认识就行，不需要会做**

- [ ] **Day 4**：参数高效微调（认知级）
  - LoRA / QLoRA（**知道有这东西**）
  - 量化（INT8 / INT4）
  - Adapter

- [ ] **Day 5**：跑通一个开源模型
  - 用 HF 调一个小模型（如 Qwen2.5-0.5B、Llama-3.2-1B）
  - 本地推理 + Prompt 实验

#### 📚 推荐资源
- [HuggingFace Course](https://huggingface.co/learn/llm-course)
- 中文资源：[Datawhale 《大模型基础》](https://github.com/datawhalechina/so-large-lm)

---

## ✅ 阶段完成标准

完成本阶段后，应该能做到：

- [ ] 一张白纸 + 一支笔，画出 Transformer 架构图并讲清楚
- [ ] 解释 Attention 是什么（白话版 + 公式版）
- [ ] 说出 GPT / BERT / Llama 的区别
- [ ] 用 HuggingFace 跑通一个开源模型
- [ ] 理解 Token、Context、Temperature 是什么
- [ ] **能给团队做一次 30 分钟的"LLM 工作原理"分享**（这是终极测试）

---

## 🎯 笔记重点

本阶段建议沉淀的笔记（放在 `笔记/` 目录下）：

- `Attention机制详解.md`
- `Transformer架构图.md`
- `GPT-BERT-Llama对比.md`
- `LLM推理参数(Temperature等).md`
- `HuggingFace使用速查.md`

---

## ⏭️ 下一阶段

完成本阶段后，进入 [阶段 3 · Spring AI 与 RAG](../03-SpringAI与RAG/README.md) ⭐ **核心阶段**
