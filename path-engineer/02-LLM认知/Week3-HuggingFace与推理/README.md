# Week 3 · HuggingFace + LLM 推理原理（5 天）

> 🎯 **本周目标**：会用 HuggingFace 加载并跑通开源 LLM，理解推理参数怎么影响输出
>
> ⏱️ **时间预算**：5 天 × 1.5h = 7.5 小时（工作日晚上）+ 周末复盘 1.5h，共约 9h
>
> 🚪 **本周地位**：从"看懂原理"到"动手玩模型"的桥梁——学完后你能本地跑 Qwen / Llama，并向团队解释每个推理参数

---

## 📌 心法（先看这个）

### 1. 这周到底学到什么程度

| ✅ 应该达到的 | ❌ 不要追求的 |
|------------|------------|
| 用 HuggingFace 三件套加载任意开源模型 | 自己实现 transformers 库 |
| 解释清楚 Temperature / Top-p / Top-k 的作用 | 推导核采样的数学证明 |
| 知道 Pre-train → SFT → RLHF 全流程 | 真的去做 RLHF |
| 知道 LoRA / QLoRA 解决什么问题 | 本周亲手训一个 LoRA |
| 在本地跑通 Qwen2.5-0.5B 或 Llama-3.2-1B | 在本地跑 70B 大模型 |

### 2. 学习方式：**玩参数 + 看效果**

每个知识点的套路：

```
1. 5 分钟读概念（一句话能讲清楚）
2. 用 HuggingFace 跑一段代码
3. 改参数（Temperature 0.0 → 1.0），看输出怎么变
4. 用自己的话总结"什么场景用什么值"
```

### 3. 心理建设

> **第一天 HuggingFace pipeline 一行代码就能跑通模型** —— 你会有种"原来 LLM 这么简单"的错觉。
>
> **第二天玩 Temperature/Top-p**，你会真切感受到 LLM 的随机性是怎么来的。
>
> **第五天本地跑通 Qwen-0.5B**，整个阶段 2 通关——你已经具备进入阶段 3（RAG 项目）的全部认知储备。

---

## 🪜 学习起点

完成 Week 1-2 后你已经具备的：

- ✅ PyTorch 训练循环（[Week 1](../Week1-神经网络与PyTorch/)）
- ✅ Transformer 架构 + 三大流派（[Week 2](../Week2-Transformer/)）
- ✅ 知道 GPT 自回归是"一个 token 一个 token 吐出来的"

> 💡 这意味着：本周你不是"从零学 LLM"，而是**站在 Transformer 架构图上，看每个推理参数控制了哪一步**。

---

## 🗓️ 5 天规划速览

| 天 | 主题 | 核心内容 | 产出 |
|----|------|---------|------|
| **Day 1** | [HuggingFace 三件套](./Day1-HuggingFace三件套.md) | `transformers` + `tokenizers` + `datasets` + `pipeline` | 一行代码跑通文本生成 |
| **Day 2** | [LLM 推理参数](./Day2-LLM推理参数.md) ⭐ | Temperature / Top-p / Top-k / max_tokens / Context Window | **一张参数速查表** |
| **Day 3** | [训练范式（认知级）](./Day3-训练范式全流程.md) | Pre-training → SFT → RLHF / DPO | 一张三阶段训练流程图 |
| **Day 4** | [参数高效微调（认知级）](./Day4-LoRA与量化.md) | LoRA / QLoRA / 量化（INT8/INT4）/ Adapter | LoRA 一图解原理 |
| **Day 5** | [本地跑通开源模型](./Day5-本地跑通开源模型.md) ⭐ | Qwen2.5-0.5B / Llama-3.2-1B 推理 + Prompt 实验 | **本地能跑的对话脚本** |

---

## 📦 配套资源

### 必备工具

| 工具 | 用途 | 安装 |
|------|------|------|
| **transformers** | HuggingFace 主库 | `pip install transformers` |
| **accelerate** | 自动设备映射 | `pip install accelerate` |
| **bitsandbytes**（可选）| 量化加载 INT8/INT4 | `pip install bitsandbytes`（仅 Linux/CUDA）|
| **modelscope**（可选）| 国内模型镜像（强烈推荐）| `pip install modelscope` |

> 💡 **国内网络下载模型**：HuggingFace Hub 国内访问较慢，**强烈推荐用 ModelScope 镜像**（魔搭社区，阿里出品），或设置 `HF_ENDPOINT=https://hf-mirror.com`。

### 模型选择建议（本周用）

| 模型 | 参数量 | 显存需求（FP16）| 适用场景 |
|------|--------|----------------|---------|
| **Qwen2.5-0.5B-Instruct** ⭐ | 0.5B | ~1GB | 中文友好，CPU 都能跑 |
| **Llama-3.2-1B-Instruct** | 1B | ~2GB | 英文为主，社区生态 |
| **Qwen2.5-1.5B-Instruct** | 1.5B | ~3GB | 效果略好，需 4GB+ 显存 |
| TinyLlama-1.1B | 1.1B | ~2GB | 学习 Llama 架构 |

> 🎯 **Mac 用户**：M1/M2/M3 用 `device_map="mps"` 加速，跑 0.5B / 1B 模型完全够。
>
> 🎯 **CPU only**：选 Qwen2.5-0.5B，跑得动但慢，做参数实验够用。

### 推荐资源（精挑）

| 资源 | 形式 | 时长 | 推荐度 |
|------|------|------|------|
| 🥇 [HuggingFace LLM Course](https://huggingface.co/learn/llm-course) | 在线 | Chapter 1-3 必看 | ⭐⭐⭐⭐⭐ |
| 🥇 [HuggingFace Transformers 文档 - Quick Tour](https://huggingface.co/docs/transformers/quicktour) | 文档 | 30 min | ⭐⭐⭐⭐⭐ |
| 🥈 [Datawhale《大模型基础》第 4-5 章](https://github.com/datawhalechina/so-large-lm) | 中文 | 选读 | ⭐⭐⭐⭐ |
| 🥈 [LoRA 论文图解（HuggingFace 官方）](https://huggingface.co/docs/peft/conceptual_guides/lora) | 文档 | 10 min | ⭐⭐⭐⭐ |
| 选看 [Karpathy - State of GPT](https://www.youtube.com/watch?v=bZQun8Y4L2A) | 视频 | 1h | ⭐⭐⭐⭐⭐（训练流程最佳讲解）|

> 💡 **本周策略**：以**本目录的 Day 1~5 教程**为主线，HuggingFace 文档当查询手册。**Karpathy 那期视频如果时间够，强烈推荐看完——胜过读 10 篇文章**。

---

## 🎯 本周完成标准（自测）

学完这 5 天，你应该能做到：

- [ ] **会用 `pipeline()` 一行调用模型**：文本生成、文本分类、问答
- [ ] **解释 Tokenizer 在做什么**：字符 → token id 的过程
- [ ] **解释 Temperature 0 / 0.7 / 1.5 输出有什么区别**
- [ ] **二选一时知道 Top-p 还是 Top-k**：能讲出工程默认值
- [ ] **画出 Pre-train → SFT → RLHF 的三阶段流程**
- [ ] **解释 LoRA 在哪里加东西**：`W = W₀ + BA`
- [ ] **知道 INT8 / INT4 量化的代价**：精度换显存
- [ ] **本地跑通一个 < 2B 的开源 LLM**：能对话、能改参数实验
- [ ] **完成阶段 2 终极测试**：能写出 30 分钟"LLM 工作原理"分享提纲

---

## 🚀 开始学习

### 推荐节奏

```
工作日晚上（每天 1.5h）：
  20:00 - 20:20  快速浏览当天 Day{N}.md
  20:20 - 21:10  跟着代码跑 + 改参数实验
  21:10 - 21:30  做当天练习题（练习/dayN_*.py）

周末（额外 1.5h）：
  - Day 5 把模型跑通后，做一次完整 Prompt 实验：
    同一个问题用 5 个不同 Temperature 跑，看输出差异
  - 整理本阶段终极笔记：《30 分钟 LLM 分享提纲》（写完讲给自己听）
```

### 第一步

👉 现在打开 [Day 1 · HuggingFace 三件套](./Day1-HuggingFace三件套.md) 开始学习。

---

## 🆘 卡住了怎么办？

| 情况 | 解决方式 |
|------|---------|
| 模型下载特别慢 | 用 `HF_ENDPOINT=https://hf-mirror.com` 或改用 ModelScope |
| 显存不够（OOM）| 1) 换更小模型（0.5B） 2) 用 `torch_dtype=torch.float16` 3) 用量化加载 |
| Mac 跑不动 | 用 `device_map="mps"`；或选 0.5B 量级模型 |
| `pipeline` 中文输出乱码 | 检查 tokenizer 是否支持中文（用 Qwen 而不是英文模型）|
| Temperature 调到 0 还有随机 | 用 `do_sample=False` 走贪婪解码 |
| LoRA 看不懂 | Day 4 只需"知道是什么"，不需要会做——阶段 5 才会真上手 |

---

## 🧭 本周与后续阶段的衔接

学完本周后，下面这些工程能力你都能丝滑承接：

| 后续话题 | 本周哪里建立的认知 |
|---------|------------------|
| RAG 调用 LLM（阶段 3）| Day 1-2：会用 HF + 知道推理参数 |
| 模型选型（阶段 3-4）| Day 5：跑过几个开源模型，知道差异 |
| LoRA 微调实战（阶段 5）| Day 4：理论认知已有，直接上手 PEFT 库 |
| 控制 LLM 输出稳定性（阶段 3 RAG）| Day 2：Temperature=0 + Top-p 0.9 的工程默认值 |
| 模型部署 / 量化推理（阶段 6）| Day 4：已知 INT8/INT4 量化的代价 |

---

## 🎓 阶段 2 通关测试（本周完成后做）

在 `02-LLM认知/笔记/` 下沉淀以下笔记：

- [ ] `Attention机制详解.md`（来自 Week 2）
- [ ] `Transformer架构图.md`（来自 Week 2）
- [ ] `GPT-BERT-Llama对比.md`（来自 Week 2）
- [ ] `LLM推理参数速查.md`（来自 Week 3 Day 2）
- [ ] `HuggingFace使用速查.md`（来自 Week 3 Day 1）
- [ ] `LoRA与量化认知卡.md`（来自 Week 3 Day 4）
- [ ] 🎤 **《30 分钟 LLM 工作原理分享提纲》**（终极测试）

> 💡 笔记的标准：**离开 3 个月再回来看，能 5 分钟想起来。**

---

## 🔗 相关链接

- ⬆️ [回到阶段 2 总览](../README.md)
- ⬅️ [Week 2 · Transformer](../Week2-Transformer/README.md)
- ➡️ [阶段 3 · Spring AI 与 RAG](../../03-SpringAI与RAG/README.md) ⭐ 第一个简历项目
- 📋 [path-engineer 主路径](../../README.md)
