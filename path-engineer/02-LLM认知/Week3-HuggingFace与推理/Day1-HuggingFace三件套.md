# Day 1 · HuggingFace 三件套（一行代码用上 LLM）

> ⏱️ 时间：1.5 小时
> 🎯 目标：能用 HuggingFace 三件套把任意开源模型跑起来
> 📋 练习：[`练习/day1_pipeline速通.py`](./练习/day1_pipeline速通.py)

---

## 0. 心法（5 分钟）

> **HuggingFace = AI 界的 Maven 中央仓库 + Spring Boot Starter。**

它干两件事：

1. **托管模型**：50 万+ 开源模型免费下载（Llama / Qwen / BERT / Whisper ……）
2. **统一 API**：不管什么模型，加载、推理、训练都是同一套代码

> 🧠 **Java 类比**：
> - HuggingFace Hub ↔ Maven Central
> - `transformers` 库 ↔ Spring Boot（封装了底层细节）
> - `pipeline()` ↔ Spring Boot 的"约定大于配置"——一行代码搞定 80% 场景

---

## 1. 三件套各司其职（10 分钟）

```
┌──────────────────────────────────────────────────────────────┐
│                  HuggingFace 三件套                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📦 transformers   ←  模型本体（Llama / Qwen / BERT …）     │
│                       AutoModel / AutoTokenizer              │
│                                                              │
│  🔤 tokenizers     ←  分词器（文本 → token id）             │
│                       负责 BPE / WordPiece 等编码           │
│                                                              │
│  📚 datasets       ←  数据集（GLUE / Wiki / 自己的 CSV）    │
│                       一行加载 + 流式读取                    │
│                                                              │
│  🛠️ accelerate     ←  设备调度（自动分配 GPU / 多卡）        │
│                                                              │
│  🎯 peft           ←  参数高效微调（LoRA / Adapter）         │
│                       Day 4 会讲                             │
└──────────────────────────────────────────────────────────────┘
```

> 💡 **本周用前两个就够**——`transformers` + `tokenizers`，其他看 Day 4-5 时再说。

---

## 2. 第一行代码：pipeline 一行通天（15 分钟）

### 2.1 文本生成

```python
from transformers import pipeline

# 一行代码：加载 + 生成（首次会自动下载模型）
generator = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
result = generator("北京的著名景点有", max_new_tokens=50)
print(result[0]["generated_text"])
```

> 💡 **就这么简单**——模型加载、tokenize、forward、decode 全部 pipeline 帮你做了。

### 2.2 其他常用 pipeline 任务

```python
# 1. 文本分类（情感分析）
classifier = pipeline("sentiment-analysis")
classifier("I love this movie!")
# → [{'label': 'POSITIVE', 'score': 0.999}]

# 2. 命名实体识别
ner = pipeline("ner")
ner("Hugging Face is based in New York.")

# 3. 问答（抽取式）
qa = pipeline("question-answering")
qa(question="Who founded Apple?",
   context="Steve Jobs founded Apple in 1976.")
# → {'answer': 'Steve Jobs', 'score': 0.98, ...}

# 4. 文本翻译
translator = pipeline("translation_en_to_zh", model="Helsinki-NLP/opus-mt-en-zh")
translator("Machine learning is fun.")

# 5. 文本摘要
summarizer = pipeline("summarization")
summarizer("一段长文本……")

# 6. 零样本分类（不用训练）
zsc = pipeline("zero-shot-classification")
zsc("我想退货", candidate_labels=["售后", "下单", "投诉"])
```

> 🎯 **`pipeline` 的本质**：把 **`tokenizer + model + post-processing`** 三步打包成一个调用。
>
> **生产环境也常用**——只要任务不复杂，pipeline 就够。

---

## 3. 拆开 pipeline 看里面（25 分钟）

> 这是本日最重要的一节——**让 pipeline 不再是黑盒**。

### 3.1 手动三步走（pipeline 内部就是这样）

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "Qwen/Qwen2.5-0.5B-Instruct"

# ① 加载分词器
tokenizer = AutoTokenizer.from_pretrained(model_id)

# ② 加载模型
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,        # FP16 省显存
    device_map="auto",                # 自动选 cpu / cuda / mps
)

# ③ 三步：tokenize → forward → decode
text = "北京的著名景点有"
inputs = tokenizer(text, return_tensors="pt").to(model.device)   # 字符串 → token id

# 生成
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    do_sample=False,                  # 贪婪解码（确定性）
)

# token id → 字符串
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 3.2 看清楚 Tokenizer 在干什么

```python
text = "Hello, 你好！"

# 编码
tokens = tokenizer.tokenize(text)
ids = tokenizer.encode(text)
print(f"text:   {text}")
print(f"tokens: {tokens}")
print(f"ids:    {ids}")

# 解码
print(f"decode: {tokenizer.decode(ids)}")
```

输出（Qwen 的 BPE 分词器）：

```
text:   Hello, 你好！
tokens: ['Hello', ',', ' 你好', '！']
ids:    [9707, 11, 220, 108386, 6313]
decode: Hello, 你好！
```

> 💡 **关键认知**：
> - 一个汉字可能是 1 个 token，也可能是多个（取决于 tokenizer 训练数据）
> - 一个英文单词可能被拆成多段（subword）
> - **token ≠ 字 ≠ 词**——这是为什么计费按 token 算，"今天天气"可能就 4 个 token，而 "antidisestablishmentarianism" 也可能 4 个 token

### 3.3 看模型输出的形状

```python
inputs = tokenizer("Hello", return_tensors="pt").to(model.device)
print(f"input_ids: {inputs.input_ids.shape}")        # (1, L)

with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits
print(f"logits: {logits.shape}")                     # (1, L, vocab_size)
# vocab_size 是词表大小，每个位置都输出一个概率分布
```

> 🎯 **回到 Week 2**：`logits` 的形状 `(B, L, vocab_size)` 你应该非常熟悉——这就是 Day 4 TinyGPT 的输出！HuggingFace 模型只是规模放大版。

---

## 4. AutoXxx 系列的设计哲学（10 分钟）

> HuggingFace 的精髓：**一套 API 适配所有模型**——这是它能成为事实标准的核心原因。

| Auto 类 | 干什么 | 例子 |
|---------|-------|------|
| `AutoTokenizer` | 自动加载对应模型的 tokenizer | Qwen → Qwen tokenizer，Llama → Llama tokenizer |
| `AutoModel` | 加载基础模型（无任务头）| 输出 hidden states |
| `AutoModelForCausalLM` ⭐ | **GPT 类模型（解码生成）** | Qwen / Llama / GPT-2 |
| `AutoModelForSequenceClassification` | 分类任务 | 情感分析 |
| `AutoModelForQuestionAnswering` | 抽取式 QA | BERT QA |
| `AutoModelForSeq2SeqLM` | Encoder-Decoder | T5 / BART |

> 💡 **本周 90% 时间用 `AutoModelForCausalLM`**——它是所有现代 LLM 的入口。

### 一个有用的小细节：`from_pretrained` 的常用参数

```python
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,         # 半精度，显存减半
    device_map="auto",                 # 自动设备分配
    trust_remote_code=True,            # 某些模型（Qwen 早期版本）需要
    cache_dir="./models",              # 自定义缓存目录
)
```

---

## 5. 中国大陆下载技巧（10 分钟）

### 5.1 方案 A：HuggingFace 镜像（推荐）

```bash
# 一次性环境变量
export HF_ENDPOINT=https://hf-mirror.com

# 或者写到 ~/.zshrc / ~/.bashrc 永久生效
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.zshrc
```

之后所有 `from_pretrained` 调用都会从镜像下载，速度可达 100MB/s。

### 5.2 方案 B：ModelScope（魔搭，阿里出品）

```python
from modelscope import AutoTokenizer, AutoModelForCausalLM

# API 跟 transformers 一模一样，只是改了 import
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
```

> 💡 **Qwen 系列建议直接用 ModelScope**——是阿里官方仓库，更新最快、稳定性最好。

### 5.3 方案 C：手动下载 + 本地路径

```bash
# 用 huggingface-cli 下载到本地
huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct --local-dir ./models/qwen-0.5b
```

```python
# 加载本地路径
tokenizer = AutoTokenizer.from_pretrained("./models/qwen-0.5b")
model = AutoModelForCausalLM.from_pretrained("./models/qwen-0.5b")
```

---

## 6. 一段完整可运行代码（10 分钟）

```python
"""
最简版本：本地跑通 Qwen2.5-0.5B 对话
首次运行会下载约 1GB
"""
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 自动选设备
device = "cuda" if torch.cuda.is_available() else (
    "mps" if torch.backends.mps.is_available() else "cpu"
)
print(f"使用设备: {device}")

# 加载
model_id = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if device != "cpu" else torch.float32,
).to(device)

# 用 chat template（Qwen / Llama-Instruct 都有）
messages = [
    {"role": "system", "content": "你是一个简洁友好的 AI 助手。"},
    {"role": "user", "content": "用一句话解释什么是机器学习"},
]

text = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
print("─" * 50)
print("Chat template 渲染后的 prompt：")
print(text)
print("─" * 50)

inputs = tokenizer(text, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,           # 贪婪解码
    )

# 只取新生成的部分
new_tokens = outputs[0][inputs.input_ids.shape[1]:]
print(tokenizer.decode(new_tokens, skip_special_tokens=True))
```

> 💡 **本周后面所有的实验都基于这段代码改**——把它存好。

---

## 7. 必看资源

| 资源 | 推荐看法 |
|------|---------|
| 🥇 [HuggingFace Quick Tour](https://huggingface.co/docs/transformers/quicktour) | 30 min，本日内容的官方版本 |
| 🥈 [HuggingFace LLM Course Chapter 1](https://huggingface.co/learn/llm-course/chapter1) | 系统讲 pipeline + 任务类型 |
| 🥉 [Tokenizer 在线可视化](https://platform.openai.com/tokenizer) | 输入文本看 token 切分，**强烈推荐玩一下** |

---

## 8. 检查清单（睡前问自己）

- [ ] 用 `pipeline` 一行调用 3 种不同任务（生成 / 分类 / NER）
- [ ] 解释 `pipeline` 内部三步：tokenize → forward → decode
- [ ] 解释 token 和字、词的关系（用例子）
- [ ] 知道 `AutoModelForCausalLM` 用在 GPT/Llama 类模型
- [ ] 配置好 HF 镜像 / ModelScope，能稳定下载模型
- [ ] 跑通 §6 的完整代码，看到模型回答出现

完成了 ➡️ [Day 2 · LLM 推理参数](./Day2-LLM推理参数.md)

---

## 🔗 相关链接

- ⬆️ [Week 3 总览](./README.md)
- ➡️ [Day 2 · LLM 推理参数](./Day2-LLM推理参数.md)
- 📝 [本日练习](./练习/day1_pipeline速通.py)
