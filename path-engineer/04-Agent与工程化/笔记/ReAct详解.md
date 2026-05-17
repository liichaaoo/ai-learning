# ReAct 详解（速查手册）

> 服务于 Week 2 + 阶段 4 Agent 项目。

---

## 1. 一句话本质

> **ReAct = Reasoning + Acting，"想一步、做一步、看一眼、再想"——LLM 跟工具的对话循环。**

---

## 2. 三段论

```
Thought    （想）：下一步要做什么
Action     （做）：调用某个工具 + 参数
Observation（看）：工具返回什么
   ↓
   下一轮 Thought（看结果再想）
```

直到 LLM 觉得"够了"，输出 Final Answer。

---

## 3. ReAct vs CoT

| 维度 | CoT | ReAct |
|------|-----|-------|
| 推理方式 | 一口气写完 | 走一步看一步 |
| 能否调工具 | ❌ | ✅ |
| 适合 | 数学题、纯推理 | 需要外部信息的任务 |
| 错误纠正 | 全错重来 | 一步错可调整 |

---

## 4. 两种实现

### A. 手写文本协议（教学）

```
Thought: ...
Action: weather({"city": "上海"})

→ 你 parse 出 weather 调用 → 拼回去：
Observation: 上海 18°C 晴

→ 模型再输出：
Thought: ...
Final Answer: ...
```

### B. Function Calling（生产）

```java
// 直接用 LangChain4j 的 AiServices + tools
AiServices.builder(Assistant.class)
        .chatLanguageModel(model)
        .tools(weatherTool, calcTool)
        .build();
```

**本质都是 ReAct**——只是 B 用 OpenAI 的 JSON tool_calls 协议，更稳。

---

## 5. 死循环 4 招防御

```
① maxSteps（如 10）
② 重复检测：连续 2 次同 tool 同 args → 强制结束
③ Prompt 约束："如有足够信息，直接输出 Final Answer"
④ 监控：tool_call_count > 阈值 告警
```

---

## 6. 工程优化

| 招式 | 收益 |
|------|------|
| 减少工具数量（< 10）| 选错率降 |
| 工具描述写"何时调" | 选对率升 |
| 加 system prompt 约束范围 | 避免乱调 |
| 缓存 (问题, 工具调用序列) | 降成本 |
| 流式输出中途 token | 用户体感快 |

---

## 7. 高频面试题

**Q：ReAct 三段论？**
Thought → Action → Observation 循环。

**Q：跟 CoT 的本质区别？**
CoT 独白，ReAct 跟工具对话。

**Q：怎么防死循环？**
maxSteps + 重复检测 + Prompt 约束 + 监控告警。

**Q：生产用文本协议还是 Function Calling？**
Function Calling（稳）；学习时手写一遍文本协议（懂）。

**Q：Plan-and-Execute 比 ReAct 好在哪？**
适合复杂多步任务，能给用户进度推送，但 Token 消耗更高。

---

## 🔗 相关链接

- 📖 [Week 2 Day 1 · ReAct 模式](../Week2-Agent设计模式/Day1-ReAct模式.md)
- 📚 [ReAct 论文](https://arxiv.org/abs/2210.03629)
