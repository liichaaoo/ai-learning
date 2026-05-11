# 阶段 4：大模型核心技术

> 周期：2-3 个月｜目标：理解 LLM 训练全流程 + 能微调和部署

---

## 子目录

```
04-阶段4-大模型核心技术/
├── 4.1-预训练/          # Scaling Law、数据工程、分布式训练
├── 4.2-SFT与RLHF/       # SFT、奖励模型、PPO、DPO/GRPO
├── 4.3-PEFT-LoRA/       # LoRA、QLoRA、Adapter
├── 4.4-推理优化/        # KV Cache、量化、vLLM、SGLang
├── 论文/
├── 资料/
├── 笔记/
├── 代码/
└── 产出/
```

---

## 必读论文/技术报告
- **LLaMA 1 / 2 / 3**
- **Qwen 系列**（Qwen2/Qwen2.5/Qwen3 技术报告）
- **DeepSeek-V2 / V3 / R1**
- **Mixtral**（MoE 经典）
- **LoRA / QLoRA**
- **InstructGPT**（RLHF 奠基）
- **DPO**

---

## 核心框架
- 训练：DeepSpeed、Megatron-LM、PyTorch FSDP
- 微调：LLaMA-Factory、PEFT、TRL
- 推理：**vLLM**、SGLang、TensorRT-LLM
- 量化：GPTQ、AWQ、bitsandbytes

---

## 产出要求
- [ ] **LoRA 微调开源模型**（如 Qwen2-7B）完成特定任务
- [ ] **vLLM 部署推理服务**
- [ ] 完成一次 DPO 训练
- [ ] 论文精读笔记 ≥ 5 篇
