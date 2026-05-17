"""
Day 5 练习 · 本地多轮对话脚本（阶段 2 终极交付物）⭐

目标：跑通这个脚本 = 完成阶段 2。
- 多轮对话（保留上下文）
- 自动设备选择（CUDA / MPS / CPU）
- 内置参数实验模式

完成方式：
1. 设置好 HF_ENDPOINT 镜像（中国大陆）
2. 直接运行：python day5_本地对话脚本.py
3. 在交互中尝试以下指令：
   - 普通对话
   - "/temp 0.0"  切换到贪婪
   - "/temp 1.5"  切换到高温
   - "/clear"     清空历史
   - "/exit"      退出

📖 对应教程：../Day5-本地跑通开源模型.md
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# ═══════════════════ 配置 ═══════════════════
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
SYSTEM_PROMPT = "你是一个简洁、友好的 AI 助手。回答尽量在 100 字以内。"

DEFAULT_GEN_KWARGS = dict(
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.05,
)


# ═══════════════════ 设备选择 ═══════════════════
def pick_device():
    if torch.cuda.is_available():
        return "cuda", torch.float16
    if torch.backends.mps.is_available():
        return "mps", torch.float16
    return "cpu", torch.float32


# ═══════════════════ 主对话循环 ═══════════════════
def chat_loop():
    device, dtype = pick_device()
    print(f"📦 设备: {device}  数据类型: {dtype}")
    print(f"⏳ 加载模型: {MODEL_ID}（首次下载约 1GB）")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=dtype).to(device)
    model.eval()
    print("✓ 模型加载完成\n")
    print("─" * 60)
    print("指令：")
    print("  /temp <值>   切换温度（如 /temp 0.0 走贪婪）")
    print("  /clear       清空对话历史")
    print("  /show        显示当前生成参数")
    print("  /exit        退出")
    print("─" * 60 + "\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    gen_kwargs = dict(DEFAULT_GEN_KWARGS)

    while True:
        try:
            user = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user:
            continue

        # ─── 处理指令 ───
        if user == "/exit":
            print("再见！")
            break
        if user == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("✓ 历史已清空\n")
            continue
        if user == "/show":
            print(f"  当前参数: {gen_kwargs}\n")
            continue
        if user.startswith("/temp "):
            try:
                t = float(user.split()[1])
                if t == 0.0:
                    gen_kwargs["do_sample"] = False
                else:
                    gen_kwargs["do_sample"] = True
                    gen_kwargs["temperature"] = t
                print(f"✓ Temperature → {t}\n")
            except (IndexError, ValueError):
                print("用法: /temp <数字>，例如 /temp 0.7\n")
            continue

        # ─── 普通对话：调模型 ───
        messages.append({"role": "user", "content": user})
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            out = model.generate(**inputs, **gen_kwargs)
        new_tokens = out[0][inputs.input_ids.shape[1]:]
        reply = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        print(f"AI：{reply}\n")
        messages.append({"role": "assistant", "content": reply})


# ═══════════════════ 自检挑战 ═══════════════════
SELF_CHALLENGE = """
─── 阶段 2 终极自检 ───

完成对话脚本后，做以下挑战：

[多轮对话验证]
  1. 对它说："你好，我叫小明"
  2. 然后问："我叫什么名字？"
  3. 它应该正确回答"小明" → 多轮上下文功能正常 ✓

[参数实验]
  4. /temp 0.0   → 提同一个开放问题 3 次，输出应该完全一样
  5. /temp 1.2   → 同问题，每次都应该不同

[Prompt 实验]
  6. 让它用一句话解释 Transformer
  7. 让它用 100 字解释 Self-Attention
  8. 让它用打油诗的形式介绍机器学习
  → 体会"换 Prompt 就能换风格"

[终极测试 - 你的 30 分钟分享]
  打开你笔记里的《30分钟LLM分享提纲.md》，对着白板讲一遍。
  讲完，阶段 2 通关 ✅
"""


if __name__ == "__main__":
    print(SELF_CHALLENGE)
    print("\n按回车开始对话...")
    input()
    chat_loop()
