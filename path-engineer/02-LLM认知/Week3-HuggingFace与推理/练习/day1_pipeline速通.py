"""
Day 1 练习 · HuggingFace pipeline 速通

目标：用 pipeline + AutoModel 各跑一遍，看清楚 HuggingFace 的 API 套路。

完成方式：
1. 把每个 TODO 填完
2. 运行：python day1_pipeline速通.py
3. 首次会下载模型（~ 1GB），耐心等

📖 对应教程：../Day1-HuggingFace三件套.md

🌐 中国大陆建议设置：
   export HF_ENDPOINT=https://hf-mirror.com
"""
import torch


# ─────────────────────────────────────────────────────────────────
# 题 1：用 pipeline 跑一段文本生成（一行通天）
# ─────────────────────────────────────────────────────────────────
def task1_pipeline():
    """
    TODO：
      1. 从 transformers 导入 pipeline
      2. 创建 text-generation pipeline，model="Qwen/Qwen2.5-0.5B-Instruct"
      3. 用 prompt = "用一句话解释什么是 Transformer：" 生成
      4. 设置 max_new_tokens=80, do_sample=False（贪婪）
      5. print 出来
    """
    print("== 题 1：pipeline 文本生成 ==")
    # 你的代码
    pass


# ─────────────────────────────────────────────────────────────────
# 题 2：手动三步走（拆开 pipeline 看里面）
# ─────────────────────────────────────────────────────────────────
def task2_manual():
    """
    TODO：手动跑一遍三步走
      1. 导入 AutoTokenizer, AutoModelForCausalLM
      2. 加载 tokenizer 和 model（同样的 model_id）
      3. tokenize："今天天气真"
      4. model.generate(max_new_tokens=20, do_sample=False)
      5. decode 出来
    打印输入字符串、token id、输出字符串
    """
    print("\n== 题 2：手动三步走 ==")
    # 你的代码
    pass


# ─────────────────────────────────────────────────────────────────
# 题 3：观察 tokenizer 的工作
# ─────────────────────────────────────────────────────────────────
def task3_tokenizer():
    """
    用 Qwen 的 tokenizer 处理 3 个文本：
      1. "Hello world"
      2. "你好世界"
      3. "antidisestablishmentarianism"  ← 看英文怎么切

    打印每个的 tokens（用 .tokenize()）和 ids（用 .encode()）
    """
    print("\n== 题 3：tokenizer 实验 ==")
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    texts = ["Hello world", "你好世界", "antidisestablishmentarianism"]
    for text in texts:
        # TODO：调用 tokenize 和 encode
        # tokens = tokenizer.tokenize(text)
        # ids = tokenizer.encode(text)
        # 你的代码
        pass


# ─────────────────────────────────────────────────────────────────
# 题 4：用 chat_template 渲染对话（Instruct 模型必备）
# ─────────────────────────────────────────────────────────────────
def task4_chat_template():
    """
    TODO：
      1. 加载 Qwen tokenizer
      2. messages = [
           {"role": "system", "content": "你是一个友好的助手"},
           {"role": "user", "content": "用一句话介绍 Python"},
         ]
      3. 用 tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
      4. 打印渲染后的 prompt（你会看到 <|im_start|> 等特殊 token）
    """
    print("\n== 题 4：chat_template ==")
    # 你的代码
    pass


# ─────────────────────────────────────────────────────────────────
# 题 5：思考题（写在注释里）
# 1. pipeline 内部到底做了哪三步？
# 2. AutoTokenizer / AutoModelForCausalLM 这种 Auto 的设计哲学是什么？
# 3. 为什么 Qwen / Llama 等 Instruct 模型必须用 chat_template，
#    不能直接拿 prompt 字符串当输入？
# ─────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    task1_pipeline()
    task2_manual()
    task3_tokenizer()
    task4_chat_template()
    print("\n✅ Day 1 通关：HuggingFace 三件套核心 API 已经能用")
