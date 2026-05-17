# Day 2 · Plan-and-Execute（规划-执行分离）

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解 P&E 跟 ReAct 的本质差异，写一个最简实现

---

## 0. 心法（5 分钟）

> **ReAct 是"走一步看一步"，P&E 是"先列计划再执行"。**

```
ReAct：
  想 → 做 → 看结果 → 想 → 做 → 看结果 → ...

Plan-and-Execute：
  ① Planner：一口气列出 1-N 步计划
  ② Executor：按计划逐步执行
  ③（可选）Replan：执行中卡壳了再调整
```

---

## 1. 什么时候用 P&E（10 分钟）

| 任务类型 | ReAct | P&E |
|---------|-------|------|
| 单工具查询（"北京天气"）| ✅ 最佳 | 杀鸡用牛刀 |
| 2-3 步组合（"查天气+判断散步"）| ✅ | 行 |
| **5+ 步复杂任务（"做市场调研报告"）** | 易跑偏 | **✅ 最佳** |
| 步骤之间有依赖（"先查 A 再算 B"）| 行 | 更好 |
| 需要给用户"中途进度"| 不行 | **✅** |

> 🎯 **判断**：任务能不能一句话拆成 3+ 步骤？能 → P&E；否则 → ReAct。

---

## 2. 最简实现（30 分钟）

### 2.1 Planner

```java
public record Step(int seq, String description, String tool, Map<String, Object> args) {}

interface Planner {
    @SystemMessage("""
            你是一个任务规划器。把用户问题拆成 1-10 个具体步骤。
            每步指明：用哪个工具、参数、为什么这一步必要。
            可用工具：search(query), calc(expr), summarize(text)
            输出 JSON 数组，不要其他文字。
            """)
    List<Step> plan(@UserMessage String userTask);
}
```

### 2.2 Executor

```java
@Service
@RequiredArgsConstructor
public class PlanExecutor {

    private final Planner planner;
    private final Map<String, ToolFunc> tools;
    private final ChatLanguageModel model;

    public String run(String task) {
        // ① 规划
        List<Step> plan = planner.plan(task);
        log.info("Plan ({} steps):\n{}", plan.size(),
            plan.stream().map(s -> "  " + s.seq() + ". " + s.description())
                .collect(Collectors.joining("\n")));

        // ② 执行（带上下文累积）
        Map<Integer, String> results = new LinkedHashMap<>();
        for (Step s : plan) {
            try {
                ToolFunc tool = tools.get(s.tool());
                String out = tool.invoke(s.args());
                results.put(s.seq(), out);
                log.info("Step {} done: {}", s.seq(), out.substring(0, Math.min(80, out.length())));
            } catch (Exception e) {
                results.put(s.seq(), "FAILED: " + e.getMessage());
                // 简单处理；复杂场景可以触发 Replan
            }
        }

        // ③ 汇总成最终答案
        String summaryPrompt = """
                用户问题：%s

                执行结果：
                %s

                请根据以上结果，给用户一个简洁、完整的回答。
                """.formatted(task,
                    results.entrySet().stream()
                        .map(e -> "步骤 " + e.getKey() + ": " + e.getValue())
                        .collect(Collectors.joining("\n")));
        return model.generate(summaryPrompt);
    }
}
```

### 2.3 调用

```java
String answer = planExecutor.run(
    "帮我调研一下电动汽车市场，输出 3 个关键趋势"
);
```

Planner 可能输出：

```json
[
  {"seq":1, "description":"搜索全球电动汽车销量数据", "tool":"search",
   "args":{"query":"global EV sales 2024"}},
  {"seq":2, "description":"搜索主要电动车厂商技术对比", "tool":"search",
   "args":{"query":"top EV makers technology comparison 2024"}},
  {"seq":3, "description":"搜索电池技术趋势", "tool":"search",
   "args":{"query":"EV battery technology trends 2024"}},
  {"seq":4, "description":"将以上数据汇总为 3 个关键趋势", "tool":"summarize",
   "args":{"text":"<前面 3 步的合并>"}}
]
```

---

## 3. Replan：执行中调整（15 分钟）

> 真实世界里，**计划总会被现实打脸**——某步失败、信息不够、新问题出现。

```java
for (int i = 0; i < plan.size(); i++) {
    Step s = plan.get(i);
    String out = execute(s);

    if (isFailed(out) || needReplan(out)) {
        // 触发重新规划
        plan = planner.replan(task, results, "Step " + s.seq() + " failed");
        i = -1;     // 从头重来（简化版；生产里更智能）
        continue;
    }
    results.put(s.seq(), out);
}
```

> 💡 **生产 P&E 必有 Replan**——否则一步错全盘崩。

---

## 4. P&E vs ReAct 工程取舍（10 分钟）

| 维度 | ReAct | P&E |
|------|-------|------|
| 实现复杂度 | 低 | 高 |
| 单次任务延迟 | 低 | **高**（Planner 多一次 LLM）|
| 复杂任务效果 | 易跑偏 | **稳** |
| 用户能看进度 | 不能 | **能（按计划逐步推送）** |
| 调试难度 | 中 | **低**（先看 Plan 对不对，再看 Execute）|
| Token 成本 | 低 | **高**（Plan 本身要钱）|

### 我的工程建议

```
任务步骤 ≤ 3   → 用 ReAct（LangChain4j 默认）
任务步骤 ≥ 5   → 用 P&E
需要进度推送   → P&E（每步完成给用户一个事件）
预算紧         → ReAct
```

---

## 5. 检查清单

- [ ] 解释 ReAct vs P&E 的本质差异
- [ ] 跑通 §2 最简 P&E（Planner + Executor）
- [ ] 故意让某步失败，触发 Replan
- [ ] 列出 P&E 的 4 个工程代价
- [ ] 知道哪些场景该选 P&E

完成了 ➡️ [Day 3 · Multi-Agent 协作](./Day3-Multi-Agent协作.md)

---

## 🔗 相关链接

- ⬅️ [Day 1 · ReAct 模式](./Day1-ReAct模式.md)
- ➡️ [Day 3 · Multi-Agent 协作](./Day3-Multi-Agent协作.md)
- ⬆️ [Week 2 总览](./README.md)
- 📚 [Plan-and-Solve 论文](https://arxiv.org/abs/2305.04091)
