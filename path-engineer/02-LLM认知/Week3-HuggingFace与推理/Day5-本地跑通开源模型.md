# Day 5 · 本地跑通开源模型 + 阶段终极测试 ⭐

> ⏱️ 时间：1.5 小时（必要时多花点也值）
> 🎯 目标：本地跑通一个 < 2B 的 LLM，做完 Prompt 实验，完成阶段 2 通关
> 📋 练习：[`练习/day5_本地对话脚本.py`](./练习/day5_本地对话脚本.py)

---

## 0. 心法（5 分钟）

> **今天不是学新东西，是把前 4 天 + Week 1-2 全部串起来。**

完成今天 = 完成阶段 2。今天产出：

```
1. 一份本地能跑的对话脚本（Qwen 0.5B 或 Llama 1B）
2. 一份 Prompt 实验报告（同问题 5 个 Temperature 对比）
3. 一份 30 分钟"LLM 工作原理"分享提纲（终极测试）
```

---

## 1. 完整对话脚本（30 分钟）

### 1.1 选择模型

| 模型 | 选谁 | 理由 |
|------|------|------|
| **CPU only / Mac** | **Qwen2.5-0.5B-Instruct** | 1GB 显存，几秒一句话 |
| **8GB GPU / Mac M2 Pro** | Qwen2.5-1.5B-Instruct / Llama-3.2-1B | 效果好不少 |
| **16GB+ GPU** | Qwen2.5-3B 或 7B（INT8）| 可以做更复杂任务 |

### 1.2 完整脚本（直接拿去跑）

```python
"""
本地对话脚本（多轮）—— 阶段 2 终极交付物
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ═══════════ 配置区 ═══════════
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"   # 也可以换 "meta-llama/Llama-3.2-1B-Instruct"
SYSTEM_PROMPT = "你是一个简洁、友好的 AI 助手。回答尽量在 100 字以内。"
GEN_KWARGS = dict(
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.05,
)

# ═══════════ 设备选择 ═══════════
if torch.cuda.is_available():
    device, dtype = "cuda", torch.float16
elif torch.backends.mps.is_available():
    device, dtype = "mps", torch.float16
else:
    device, dtype = "cpu", torch.float32
print(f"📦 设备: {device}, 数据类型: {dtype}")

# ═══════════ 加载模型 ═══════════
print(f"⏳ 加载模型: {MODEL_ID}（首次会下载）")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=dtype).to(device)
model.eval()
print("✓ 加载完成\n")

# ═══════════ 多轮对话主循环 ═══════════
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("─── 开始对话（输入 quit 退出，clear 清空历史）───\n")
while True:
    user = input("你：").strip()
    if not user:
        continue
    if user == "quit":
        break
    if user == "clear":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("✓ 已清空历史\n")
        continue

    messages.append({"role": "user", "content": user})

    # 用 chat template 渲染整段对话
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(**inputs, **GEN_KWARGS)
    new_tokens = outputs[0][inputs.input_ids.shape[1]:]
    reply = tokenizer.decode(new_tokens, skip_special_tokens=True)

    print(f"AI：{reply}\n")
    messages.append({"role": "assistant", "content": reply})
```

> 💡 **跑通后**：试一下连续追问、上下文引用，体验"它真的记得前面"。

### 1.3 跑通的标志

```
你：你好，我叫小明
AI：你好小明！很高兴认识你，有什么可以帮你的吗？

你：我叫什么名字？
AI：你叫小明！                         ← ✓ 模型记住了上下文（多轮对话生效）

你：用一句话解释 Transformer
AI：Transformer 是一种基于自注意力机制的神经网络架构……

你：quit
```

---

## 2. Prompt 实验：参数对输出的影响（25 分钟）

### 2.1 实验设计

**同一个问题，5 个 Temperature 各跑 3 次**，对比输出多样性。

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda" if torch.cuda.is_available() else "cpu")

prompt = "用一句话描述秋天的森林"
messages = [{"role": "user", "content": prompt}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

experiments = [
    ("贪婪 (T=0)",        dict(do_sample=False)),
    ("低温 (T=0.3)",      dict(do_sample=True, temperature=0.3, top_p=0.9)),
    ("默认 (T=0.7)",      dict(do_sample=True, temperature=0.7, top_p=0.9)),
    ("高温 (T=1.2)",      dict(do_sample=True, temperature=1.2, top_p=0.9)),
    ("极高温 (T=2.0)",    dict(do_sample=True, temperature=2.0, top_p=0.95)),
]

for name, kw in experiments:
    print(f"\n═══ {name} ═══")
    for i in range(3):
        torch.manual_seed(42 + i)
        out = model.generate(**inputs, max_new_tokens=80, **kw)
        reply = tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        print(f"  [{i+1}] {reply}")
```

### 2.2 你应该观察到的现象

| 实验 | 预期现象 |
|------|---------|
| T=0 | **3 次完全一样**（贪婪解码确定性）|
| T=0.3 | 3 次大体一样，偶尔换个词 |
| T=0.7 | **3 次都不一样，但都合理** ← 默认配置 |
| T=1.2 | 出现一些有趣但偶尔不通顺的表达 |
| T=2.0 | 可能开始**胡言乱语**（甚至中英文夹杂、语法乱）|

> 🎯 **跑完后把 5 组结果截图存档** —— 这是你向团队解释参数最有说服力的素材。

---

## 3. 终极测试：写一份 30 分钟"LLM 工作原理"分享提纲（25 分钟）

> **这是阶段 2 的通关测试**——能不能把前 3 周学的全部串起来，**讲给一个非 AI 的同事听懂**。

### 3.1 提纲模板（直接照抄改）

```markdown
# 30 分钟 LLM 工作原理分享 · 提纲

## 引子（3 min）
- 一句话钩子：当你问 ChatGPT "今天天气真" 它怎么知道接 "好"？
- 倒推：模型在做的是"预测下一个 token"，整个回答就是反复猜下一个词
- 今天分享会回答的 5 个问题：
  1. 文字怎么变成模型能算的东西？
  2. 模型怎么"理解"上下文？
  3. 为什么能记住对话？
  4. 我们能控制它吗？
  5. 作为工程师我们能干什么？

## 第一站：Token 化与 Embedding（5 min）
- Token：不是字也不是词
- Tokenizer 工作流（举一个具体例子，"今天天气" → [12, 45, 88]）
- Embedding：每个 token 查表得到一个 768 维向量
- → 文字进入了"数学世界"

## 第二站：Transformer 架构（8 min，最核心）
- 一张图：Attention + FFN + 残差 + LayerNorm
- Self-Attention 直觉：
  - 图书馆类比（Q/K/V）
  - softmax(QK^T/√d_k) V 一行公式
- Multi-Head：多角度看上下文
- 为什么是 Transformer 而不是 RNN：长距离 + 并行
- N 层堆叠 + 残差 = 大模型的"深度"

## 第三站：GPT 怎么生成（5 min）
- 自回归：一次一个 token，吐完一个再算下一个
- KV Cache 让推理变快
- 推理参数：Temperature / Top-p
  - 跑现场实验：T=0 vs T=0.7 vs T=2 看输出差异

## 第四站：训练全流程（5 min）
- Pre-training：互联网级文本，预测下一个 token，烧上千万美元
- SFT：教模型按指令回答
- RLHF / DPO：让回答更符合人类偏好
- 一张图说清三阶段（前面学的图）

## 第五站：作为工程师我们关心什么（3 min）
- 选模型：Qwen / Llama / GPT-4o
- 写 Prompt
- RAG（下个阶段重点）
- 微调：LoRA / QLoRA（小成本特化）
- 部署：量化 / vLLM

## 收尾（1 min）
- 一句话总结：LLM 不是魔法，是 **Transformer + 海量数据 + 三阶段训练**
- 给 Q&A 留时间

---

## 备料（不一定讲，问到了就用）
- "幻觉"为什么发生？
- 长 context 为什么贵？
- BERT 现在还重要吗？
- LoRA 是什么？
```

### 3.2 检查标准

```
✅ 能讲出来 = 真懂
❌ 只能写出来但讲不出来 = 半懂
❌ 写不出来 = 还没懂

→ 最终标准：把上面的 5 站，对着白板讲给自己听一遍。
   每一站都能开口讲清楚，就是阶段 2 通关。
```

---

## 4. 阶段 2 自检清单（10 分钟）

> 把整个阶段的认知做最后一次过筛。

### Week 1 · 神经网络与 PyTorch
- [ ] 默写训练循环 5 步：forward → loss → backward → step → zero_grad
- [ ] 解释为什么需要激活函数
- [ ] 解释 SGD 和 Adam 区别（一句话）

### Week 2 · Transformer
- [ ] 默写 `softmax(QK^T/√d_k)V`，并讲清每一步
- [ ] 画 Transformer 架构图（5 大零件）
- [ ] 解释 Multi-Head / 因果掩码 / Pre-LN
- [ ] 默写 GPT vs BERT vs Llama 三大流派对比表
- [ ] 默写 Llama 三件套：RoPE / RMSNorm / SwiGLU

### Week 3 · HuggingFace 与推理
- [ ] 用 `pipeline()` 一行调用模型
- [ ] 默写 5 大推理参数（含工程默认值）
- [ ] 解释 Pre-train → SFT → RLHF/DPO 三阶段
- [ ] 解释 LoRA：`W = W₀ + BA`
- [ ] 解释 INT8 / INT4 量化的代价
- [ ] **本地跑通 < 2B 模型并完成 Prompt 实验**
- [ ] **写出 30 分钟分享提纲**

---

## 5. 笔记沉淀（必做）

在 `02-LLM认知/笔记/` 下完成（用自己的话写，不要抄）：

- [ ] `Attention机制详解.md`
- [ ] `Transformer架构图.md`
- [ ] `GPT-BERT-Llama对比.md`
- [ ] `LLM推理参数速查.md`
- [ ] `HuggingFace使用速查.md`
- [ ] `LoRA与量化认知卡.md`
- [ ] `30分钟LLM分享提纲.md` ⭐

> 📌 **笔记标准**：3 个月后再看，5 分钟想起来。

---

## 6. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [Karpathy - Intro to LLMs (1h)](https://www.youtube.com/watch?v=zjkBMFhNj_g) | 整体认知最佳收尾视频 |
| 🥈 [Qwen 官方 GitHub](https://github.com/QwenLM/Qwen2.5) | 看 README 学最新用法 |
| 🥉 [Llama 官方 model card](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) | 学习模型卡的正确读法 |

---

## 7. 阶段 2 通关 → 进入阶段 3

恭喜你！完成了阶段 2 的全部内容。现在你应该具备：

- ✅ 看到 Transformer 论文 / 模型代码不再陌生
- ✅ 看到 LLM API 文档（OpenAI / Qwen / Claude）一眼懂参数含义
- ✅ 给团队/产品同事讲清楚 LLM 是怎么工作的
- ✅ 选模型 / 调参 / 排查"为什么模型这样回答"
- ✅ 看到 LoRA / 量化 / RLHF 等术语，能在工程对话里跟上

**下一站：[阶段 3 · Spring AI 与 RAG](../../03-SpringAI与RAG/README.md)** ⭐ **核心阶段（6 周）**

> 🎯 阶段 3 你将做出**第一个能写进简历的项目** —— 企业知识库 RAG 系统。
> 本阶段建立的 Transformer / Embedding / 推理参数 / HuggingFace 能力，会在 RAG 的每一个环节里被反复用到。

---

## 🔗 相关链接

- ⬅️ [Day 4 · LoRA 与量化](./Day4-LoRA与量化.md)
- ⬆️ [Week 3 总览](./README.md)
- ⬆️ [阶段 2 总览](../README.md)
- ➡️ [阶段 3 · Spring AI 与 RAG](../../03-SpringAI与RAG/README.md)
- 📝 [本日练习](./练习/day5_本地对话脚本.py)
