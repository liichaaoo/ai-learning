# Day 4 · LoRA + 量化（让大模型"瘦下来"）

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解 LoRA 和量化解决什么问题，知道工程取值
> 📋 练习：[`练习/day4_量化与peft.py`](./练习/day4_量化与peft.py)
>
> ⚠️ **本日是认知级**——阶段 5 才会真上手 LoRA 训练，今天只需"听过、看懂图、知道怎么用"

---

## 0. 心法（5 分钟）

> **大模型有两个"贵"：训练贵 + 推理贵。LoRA 解决训练贵，量化解决推理贵。**

```
┌─────────────────────┬──────────────────┬──────────────────┐
│        问题         │      解法         │     代价         │
├─────────────────────┼──────────────────┼──────────────────┤
│  全量微调贵         │  LoRA / QLoRA    │  几乎无损        │
│  推理显存贵         │  INT8 / INT4 量化 │  精度略降        │
│  推理速度慢         │  KV Cache, vLLM  │  几乎无损        │
└─────────────────────┴──────────────────┴──────────────────┘
```

---

## 1. 全量微调到底贵在哪（10 分钟）

假设你想微调 **Llama-3-8B**（80 亿参数）：

| 资源 | 全量微调 | 备注 |
|------|---------|------|
| **模型本体（FP16）** | 16 GB | 8B × 2 字节 |
| **梯度（FP16）** | 16 GB | 跟参数一样大 |
| **优化器状态（Adam，FP32）** | 64 GB | 2 份动量 + 1 份参数副本，3× 8B × 4 字节 |
| **激活值** | ~ 几 GB ~ 几十 GB | 跟序列长度成正比 |
| **总计** | **~ 100+ GB** | **A100 80GB 都不够** |

> 🤯 微调一个 8B 模型，**没有多张 A100/H100 都做不了**。
>
> 这就是为什么"全量微调"在工业界基本没人做——**LoRA 才是日常方案**。

---

## 2. LoRA：低秩分解的魔法 ⭐（25 分钟，本日核心）

### 2.1 LoRA 的核心思想（一图说清）

```
原始：
  权重矩阵 W₀ : (4096, 4096)，~ 16M 参数
  全量微调：直接更新 W₀ 的所有 16M 参数

LoRA：
  W₀ 冻结住（不更新）
  在旁边加两个小矩阵 A、B：
      A : (4096, 8)    ←  16M 个 → 32K 个
      B : (8,  4096)   ←
  ΔW = B · A           ←  形状还是 (4096, 4096)
  实际权重 W = W₀ + ΔW = W₀ + BA

只训练 A 和 B → 训练参数从 16M 降到 32K，缩了 500 倍！
```

### 2.2 为什么管用：低秩假设

**LoRA 论文的核心观察**：

> "微调时，权重的**实际改变量 ΔW 是低秩的**——也就是说，调整方向只在很少几个维度上发生。"

直觉理解：

```
微调 = 在已经预训练好的能力上"特化"——不是重学一切
特化的"方向"通常很窄 —— 用一个低秩矩阵表达就够了
```

### 2.3 LoRA 的工程参数

```python
# 用 PEFT 库（HuggingFace 出品）
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,                      # ⭐ rank：低秩维度（4 / 8 / 16 / 32）
    lora_alpha=16,            # 缩放因子（一般 = 2 × r）
    target_modules=[          # 给哪些层加 LoRA
        "q_proj", "k_proj",   # ⭐ 通常给 Attention 的 Q/K/V/O
        "v_proj", "o_proj",
    ],
    lora_dropout=0.05,
    bias="none",
)

model = get_peft_model(model, config)
model.print_trainable_parameters()
# trainable params: 8M ‖ all params: 8B ‖ trainable%: 0.1%
```

**参数取值经验**：

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `r`（秩） | 8 ~ 16 | 越大表达力越强但越贵 |
| `lora_alpha` | 16 ~ 32 | 通常 = 2 × r |
| `target_modules` | Q/K/V/O 投影 | 高级用法可包含 FFN |
| `lora_dropout` | 0.05 ~ 0.1 | 过拟合时调高 |

### 2.4 LoRA 训练 vs 全量微调对比

| 维度 | 全量微调 | LoRA (r=8) |
|------|---------|-----------|
| 训练参数 | 8B (100%) | ~ 8M (**0.1%**) |
| 显存（含梯度+优化器）| ~ 100 GB | ~ 24 GB |
| 训练速度 | 1× | 1.5 ~ 3× 更快 |
| 效果 | 100% | 95% ~ 100% |
| 多任务部署 | 每任务一份完整模型 | **只存 LoRA 权重（几 MB）** ⭐ |

> 🎯 **LoRA 最大的工程优势**：**几 MB 的 LoRA 权重 + 共享一个 base 模型 = 一台机器服务多个微调版本**。

### 2.5 一个 LoRA 文件长什么样

```bash
$ ls my_lora_output/
adapter_config.json    # LoRA 配置
adapter_model.bin      # ⭐ 只有 8M ~ 几十 MB（实际权重）
README.md
```

**部署时**：

```python
# 加载 base 模型
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")

# 把 LoRA 加到 base 上
from peft import PeftModel
model = PeftModel.from_pretrained(model, "my_lora_output")

# 推理：跟正常模型一样
```

> 💡 **HuggingFace 上有大量 LoRA 权重**（如 alpaca-lora）——下载一个 LoRA 就能拥有特定能力，不用下完整模型。

---

## 3. QLoRA：把 base 也压一压（10 分钟）

### 3.1 QLoRA = 量化 + LoRA

**思路**：

```
LoRA：base 模型 FP16（16 GB），LoRA 部分 FP32 训练
QLoRA：base 模型 INT4（4 GB），LoRA 部分 FP16 训练
                ↑↑↑
            量化把 base 进一步压到 1/4
```

**结果**：**24 GB 单卡可以微调 Llama-3-70B**（论文实测）。

### 3.2 QLoRA 三大技术点（听过即可）

| 技术 | 干什么 |
|------|-------|
| **NF4 量化** | 一种适合神经网络权重分布的 4-bit 表示 |
| **Double Quantization** | 连"量化常数"也量化一遍，再压 |
| **Paged Optimizer** | 显存满了自动 page 到 CPU 内存 |

> 🎯 **本周认知层**：知道 **QLoRA = 量化的 base + LoRA 微调** 即可。**阶段 5 实操时再看公式细节**。

---

## 4. 量化：把 FP16 压成 INT8/INT4（15 分钟）

### 4.1 为什么要量化

**推理瓶颈**：模型权重大 → 显存占用大 → 部署难。

```
Llama-3-70B：
  FP16:  140 GB    ← 需要 2× A100 80GB
  INT8:   70 GB    ← 1× A100 80GB
  INT4:   35 GB    ← 1× RTX 4090（24GB）+ 内存 swap 可跑
```

### 4.2 量化是什么意思

**用更少的位数存储权重**：

| 数据类型 | 每个权重占用 | 表达范围 |
|---------|------------|---------|
| FP32（默认）| 4 字节 | 极大范围、极高精度 |
| **FP16 / BF16** | **2 字节** | 训练默认（半精度）|
| **INT8** | **1 字节** | 推理常用（精度损失小）|
| **INT4** | **0.5 字节** | 极端推理（精度损失稍大）|

```
FP16 权重: 0.7234152
        ↓ INT8 量化
INT8 表示: 92 (字节)
        ↓ 反量化
近似还原: 0.7196
            (有微小误差，但对模型效果通常影响 < 1%)
```

### 4.3 量化的两条路线

| 路线 | 时机 | 代表 |
|------|------|------|
| **PTQ（训练后量化）** | 模型训练完，推理前压 | bitsandbytes / GPTQ / AWQ |
| **QAT（量化感知训练）** | 训练时就模拟低精度 | 效果更好但更贵 |

> 💡 **工程上 95% 用 PTQ**——简单、快、效果够用。

### 4.4 用 HuggingFace + bitsandbytes 一行量化加载

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# INT8 量化
bnb_config = BitsAndBytesConfig(load_in_8bit=True)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
)

# INT4 量化（QLoRA 同款配置）
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",            # 用 NF4
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
```

> ⚠️ `bitsandbytes` 目前主要支持 Linux + CUDA。**Mac 不支持 bnb 量化**——用 GGUF 格式 + llama.cpp 替代。

### 4.5 量化的代价

| 量化级别 | 显存节省 | 精度损失（PPL 上升）| 推荐场景 |
|---------|---------|------------------|---------|
| FP16 | baseline | 0% | 训练 / 高精度场景 |
| **INT8** | **50%** | < 1% | **生产推理首选** |
| **INT4** | **75%** | 2 ~ 5% | 显存极紧张时 |
| INT2 / INT1 | > 90% | 严重退化 | 实验性 |

> 🎯 **工程默认**：**INT8 是性价比之王**——半显存换 < 1% 精度损失，几乎白嫖。

---

## 5. 推理优化全家桶（5 分钟，认知层）

> 阶段 6 部署时会展开，今天先听个名字。

| 技术 | 干什么 |
|------|-------|
| **KV Cache** | 缓存历史 K/V，避免重算（本周 Day 3 提过）|
| **量化** | INT8/INT4，今天讲过 |
| **vLLM** | 高吞吐推理框架（PagedAttention）|
| **TensorRT-LLM** | NVIDIA 的极致优化推理引擎 |
| **GGUF + llama.cpp** | CPU/Mac 友好的轻量推理 |
| **Speculative Decoding** | 用小模型起草、大模型验证，加速 2-3× |

> 💡 **作为后端工程师**：阶段 6 你会真用到 **vLLM 部署** 和 **GGUF 本地推理**。

---

## 6. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [LoRA 论文图解（HuggingFace 官方）](https://huggingface.co/docs/peft/conceptual_guides/lora) | **10 分钟读完**，最清晰 |
| 🥈 [QLoRA 论文](https://arxiv.org/abs/2305.14314) | 看图 1 + 摘要即可 |
| 🥉 [bitsandbytes 文档](https://huggingface.co/docs/transformers/main/quantization/bitsandbytes) | 量化加载实操指南 |

---

## 7. 检查清单（睡前问自己）

- [ ] 解释为什么全量微调贵（4 个内存大头）
- [ ] 默写 LoRA 公式：`W = W₀ + BA`，画图说明
- [ ] 解释 LoRA 的 `r` 是什么、推荐取值
- [ ] LoRA 在工程上最大的好处（部署多任务）
- [ ] 解释 QLoRA = 什么 + 什么
- [ ] FP16 / INT8 / INT4 的存储对比 + 精度代价
- [ ] 知道 PTQ vs QAT，工程上常用哪个
- [ ] 听过 vLLM / GGUF / Speculative Decoding 这些词

完成了 ➡️ [Day 5 · 本地跑通开源模型](./Day5-本地跑通开源模型.md)

---

## 🔗 相关链接

- ⬅️ [Day 3 · 训练范式全流程](./Day3-训练范式全流程.md)
- ➡️ [Day 5 · 本地跑通开源模型](./Day5-本地跑通开源模型.md)
- ⬆️ [Week 3 总览](./README.md)
- 📝 [本日练习](./练习/day4_量化与peft.py)
