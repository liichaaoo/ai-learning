"""
Day 4 练习 · 量化与 PEFT/LoRA（认知级 + 部分实操）

目标：
1. 看见量化加载的实际显存差异（如果有 GPU）
2. 配置一次 LoRA（不实际训练，只看参数量）

完成方式：
1. 跑能跑的部分（GPU 才能跑量化、Mac 用普通 LoRA 配置）
2. 把每个 TODO 填完

📖 对应教程：../Day4-LoRA与量化.md
"""
import torch


# ─────────────────────────────────────────────────────────────────
# 题 1：对比 FP16 vs INT8 加载的显存（仅 CUDA 可跑）
# ─────────────────────────────────────────────────────────────────
def task1_quantization_comparison():
    """
    TODO（如果你有 NVIDIA GPU）：
      1. 加载 Qwen/Qwen2.5-0.5B-Instruct，分别用 FP16 和 INT8
      2. 用 torch.cuda.memory_allocated() 看显存占用
      3. 对比

    bnb 配置示例：
      from transformers import BitsAndBytesConfig
      bnb_config = BitsAndBytesConfig(load_in_8bit=True)
      model = AutoModelForCausalLM.from_pretrained(
          model_id, quantization_config=bnb_config, device_map="auto"
      )
    """
    print("== 题 1：FP16 vs INT8 显存对比 ==")
    if not torch.cuda.is_available():
        print("⚠️ 跳过：bitsandbytes 主要支持 NVIDIA CUDA，本机无 GPU/或为 Mac")
        print("   认知级：知道 INT8 显存约为 FP16 一半（量化的核心好处）")
        return

    # 你的代码
    pass


# ─────────────────────────────────────────────────────────────────
# 题 2：配置一次 LoRA，看可训练参数比例（任何机器都能跑）
# ─────────────────────────────────────────────────────────────────
def task2_lora_config():
    """
    用 PEFT 库给 Qwen-0.5B 加 LoRA，打印可训练参数。

    步骤：
      1. pip install peft（如果没装）
      2. from peft import LoraConfig, get_peft_model, TaskType
      3. config = LoraConfig(
            r=8, lora_alpha=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05, bias="none",
            task_type=TaskType.CAUSAL_LM,
         )
      4. model = AutoModelForCausalLM.from_pretrained(...)
      5. model = get_peft_model(model, config)
      6. model.print_trainable_parameters()

    期望输出大致：
      trainable params: ~ 几 M  ‖  all params: 0.5B  ‖  trainable%: ~0.5%
    """
    print("\n== 题 2：LoRA 配置 ==")
    try:
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError:
        print("⚠️ 未安装 peft，请: pip install peft")
        print("   认知级：LoRA 把可训练参数降到 1% 以内")
        return

    from transformers import AutoModelForCausalLM

    # TODO：你的代码
    pass


# ─────────────────────────────────────────────────────────────────
# 题 3：用 NumPy 模拟 LoRA 的核心思想（不需要 GPU）
# 演示：W = W₀ + B·A，B、A 是低秩小矩阵
# ─────────────────────────────────────────────────────────────────
def task3_lora_intuition():
    """
    用 NumPy 模拟 LoRA：
      原始权重 W₀ : (4096, 4096) → 16M 参数
      LoRA  A  : (4096, 8)
            B  : (8, 4096)
      W = W₀ + B @ A    形状跟 W₀ 一样

    打印：
      - W₀ 的参数量
      - LoRA (A + B) 的参数量
      - 缩减比例
    """
    print("\n== 题 3：LoRA 直觉（NumPy 模拟）==")
    import numpy as np
    np.random.seed(42)

    d = 4096
    r = 8

    W0 = np.random.randn(d, d) * 0.01   # 假装这是冻结的预训练权重
    A = np.random.randn(d, r) * 0.01
    B = np.zeros((r, d))                 # B 初始化为 0（这样开始时 BA=0，不影响 W₀）

    # TODO：
    #   1. 算 W = W0 + A @ B
    #   2. 打印 W0、A、B 各自的参数量
    #   3. 算 LoRA 减少比例 = (A.size + B.size) / W0.size
    # 你的代码

    print("\n💡 这就是为什么 LoRA 能在单卡上微调 70B 模型——"
          "训练参数只有原来的不到 1%。")


# ─────────────────────────────────────────────────────────────────
# 题 4：思考题（写在注释里）
# ─────────────────────────────────────────────────────────────────
THOUGHT_QUESTIONS = """
1. 为什么 LoRA 把 B 初始化为 0？（提示：训练开始时 BA=0，等价于没改 W₀）

2. INT8 量化精度损失 < 1%，为什么不直接全量改 INT8 训练？
   （提示：量化对梯度计算不友好，训练通常仍用 FP16/BF16）

3. QLoRA 把 base 量化到 INT4，但 LoRA 部分保持 FP16，
   为什么不把 LoRA 也量化？

4. LoRA 微调一个客服模型 + 一个翻译模型，部署时的优势是什么？
   （提示：base 共享 + LoRA 切换）
"""


if __name__ == "__main__":
    task1_quantization_comparison()
    task2_lora_config()
    task3_lora_intuition()
    print(THOUGHT_QUESTIONS)
    print("\n✅ Day 4 认知通关：阶段 5 真上手 LoRA 训练时，今天的认知会全部用上")
