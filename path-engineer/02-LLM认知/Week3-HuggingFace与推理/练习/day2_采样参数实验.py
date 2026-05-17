"""
Day 2 练习 · 采样参数实验

目标：亲眼看到 Temperature / Top-p / Top-k 对输出的影响。
不是看公式记住，是"用感觉记住"。

完成方式：
1. 跑完整脚本（不需要填 TODO，直接观察输出）
2. 把你看到的现象写到 §结尾的"观察笔记"

📖 对应教程：../Day2-LLM推理参数.md
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"


def setup():
    if torch.cuda.is_available():
        device, dtype = "cuda", torch.float16
    elif torch.backends.mps.is_available():
        device, dtype = "mps", torch.float16
    else:
        device, dtype = "cpu", torch.float32
    print(f"设备: {device}\n")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=dtype).to(device)
    model.eval()
    return tokenizer, model


def make_prompt(tokenizer, user_msg: str):
    msgs = [{"role": "user", "content": user_msg}]
    text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tokenizer(text, return_tensors="pt")


def generate(model, tokenizer, inputs, **kwargs):
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(**inputs, **kwargs)
    return tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


# ─────────────────────────────────────────────────────────────────
# 实验 1：Temperature 阶梯（同一个 prompt + 不同 T）
# ─────────────────────────────────────────────────────────────────
def exp1_temperature(model, tokenizer):
    print("═" * 60)
    print("实验 1：Temperature 阶梯（同问题，不同 T，各 3 次）")
    print("═" * 60)

    inputs = make_prompt(tokenizer, "用一句话描述秋天的森林")

    configs = [
        ("贪婪 T=0",       dict(do_sample=False)),
        ("低温 T=0.3",     dict(do_sample=True, temperature=0.3, top_p=0.9)),
        ("默认 T=0.7",     dict(do_sample=True, temperature=0.7, top_p=0.9)),
        ("高温 T=1.2",     dict(do_sample=True, temperature=1.2, top_p=0.9)),
        ("极高温 T=2.0",   dict(do_sample=True, temperature=2.0, top_p=0.95)),
    ]

    for name, kw in configs:
        print(f"\n--- {name} ---")
        for i in range(3):
            torch.manual_seed(42 + i)
            text = generate(model, tokenizer, inputs, max_new_tokens=80, **kw)
            print(f"  [{i+1}] {text[:120]}")


# ─────────────────────────────────────────────────────────────────
# 实验 2：Top-p vs Top-k 对比
# ─────────────────────────────────────────────────────────────────
def exp2_top_p_k(model, tokenizer):
    print("\n" + "═" * 60)
    print("实验 2：Top-p vs Top-k 对比")
    print("═" * 60)

    inputs = make_prompt(tokenizer, "续写一句富有想象力的话：那只猫跳上窗台，")

    configs = [
        ("Top-p=0.5（保守）",      dict(do_sample=True, temperature=1.0, top_p=0.5)),
        ("Top-p=0.9（默认）",      dict(do_sample=True, temperature=1.0, top_p=0.9)),
        ("Top-p=1.0（不截断）",    dict(do_sample=True, temperature=1.0, top_p=1.0)),
        ("Top-k=10（保守）",       dict(do_sample=True, temperature=1.0, top_k=10)),
        ("Top-k=50（默认）",       dict(do_sample=True, temperature=1.0, top_k=50)),
    ]

    for name, kw in configs:
        print(f"\n--- {name} ---")
        for i in range(2):
            torch.manual_seed(42 + i)
            text = generate(model, tokenizer, inputs, max_new_tokens=60, **kw)
            print(f"  [{i+1}] {text[:120]}")


# ─────────────────────────────────────────────────────────────────
# 实验 3：repetition_penalty 抑制重复
# ─────────────────────────────────────────────────────────────────
def exp3_repetition(model, tokenizer):
    print("\n" + "═" * 60)
    print("实验 3：repetition_penalty 抑制重复")
    print("═" * 60)

    inputs = make_prompt(tokenizer, "请连续说 5 个不同的水果名")

    for rp in [1.0, 1.1, 1.3]:
        print(f"\n--- repetition_penalty = {rp} ---")
        torch.manual_seed(42)
        text = generate(
            model, tokenizer, inputs,
            max_new_tokens=80, do_sample=True, temperature=1.0, top_p=0.9,
            repetition_penalty=rp,
        )
        print(f"  {text[:200]}")


# ─────────────────────────────────────────────────────────────────
# 观察笔记（跑完后填写！）
# ─────────────────────────────────────────────────────────────────
NOTES_TEMPLATE = """
─── 我的观察笔记（跑完实验后填写）───

实验 1 - Temperature：
  - 贪婪 (T=0)：3 次一样吗？___________________
  - 默认 (T=0.7)：多样性如何？___________________
  - 极高温 (T=2.0)：开始胡说了吗？看到的最离谱例子：___________________

实验 2 - Top-p vs Top-k：
  - Top-p=0.5 vs Top-p=1.0 哪个更"稳"？___________________
  - 你会用哪种作为生产默认？为什么？___________________

实验 3 - repetition_penalty：
  - 1.0 时输出有重复吗？___________________
  - 1.3 会不会过度多样以至于不自然？___________________

总结你的"工程默认"：
  - 严格事实（RAG）：______________________
  - 通用聊天：______________________
  - 创意场景：______________________
"""


if __name__ == "__main__":
    tokenizer, model = setup()
    exp1_temperature(model, tokenizer)
    exp2_top_p_k(model, tokenizer)
    exp3_repetition(model, tokenizer)
    print(NOTES_TEMPLATE)
    print("\n✅ Day 2 通关：你已经亲眼看到推理参数怎么影响输出")
