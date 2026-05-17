# Day 3 · Multi-Agent 协作

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解"多 Agent 分工"模式，做一个"研究小组" demo

---

## 0. 心法（5 分钟）

> **Multi-Agent = 几个专家角色 + 一个调度员，模仿人类团队工作。**

为什么单 Agent 不够？

- 单 Agent 的 Prompt 太长（要塞所有领域知识）
- 不同角色需要不同风格（研究员严谨 vs 写手有创意）
- 串行调用 + 各管一段，反而比"一个超级 Agent"更稳

---

## 1. 经典三角色架构（10 分钟）

```
              ┌─────────────────┐
              │  Orchestrator   │  调度员（你写）
              └────────┬────────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
  ┌─────────┐    ┌─────────┐      ┌─────────┐
  │Researcher│   │ Writer  │      │Reviewer │
  │ 搜资料   │   │ 写初稿   │      │ 检查/反馈│
  └─────────┘    └─────────┘      └─────────┘
```

**典型流程**：

```
1. Researcher 调 search 工具 → 拿一堆资料
2. Writer 基于资料 → 写一份初稿
3. Reviewer 阅读初稿 → 提出修改意见
4. 如果 Reviewer 不满意 → Writer 重写（最多 N 轮）
5. 最终输出
```

---

## 2. LangChain4j 实现（30 分钟）

> Multi-Agent 没有"标准框架"——本质就是**几个 AiService 互相调用**。

### 2.1 三个角色接口

```java
interface Researcher {
    @SystemMessage("""
            你是一名资深研究员。任务：根据主题搜索资料并整理。
            输出格式：JSON {topic, facts: [...], sources: [...]}
            只调用 searchTool 工具。
            """)
    Research research(@UserMessage String topic);

    record Research(String topic, List<String> facts, List<String> sources) {}
}

interface Writer {
    @SystemMessage("""
            你是一名科技专栏作家。根据研究员提供的资料写一篇 500 字的科普文章。
            风格：通俗易懂、有数字、有故事。
            """)
    String write(@UserMessage String researchJson);
}

interface Reviewer {
    @SystemMessage("""
            你是严格的编辑。审查文章：
            - 事实是否准确（对照原始资料）
            - 是否通俗易懂
            - 是否有亮点
            输出 JSON {pass: true/false, score: 1-10, feedback: "..."}
            """)
    ReviewResult review(@UserMessage String article);

    record ReviewResult(boolean pass, int score, String feedback) {}
}
```

### 2.2 Bean 配置

```java
@Configuration
@RequiredArgsConstructor
public class MultiAgentConfig {

    private final ChatLanguageModel model;
    private final SearchTool searchTool;

    @Bean
    public Researcher researcher() {
        return AiServices.builder(Researcher.class)
                .chatLanguageModel(model)
                .tools(searchTool)
                .build();
    }

    @Bean
    public Writer writer() {
        return AiServices.create(Writer.class, model);
    }

    @Bean
    public Reviewer reviewer() {
        return AiServices.create(Reviewer.class, model);
    }
}
```

### 2.3 Orchestrator（关键）

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class Orchestrator {

    private final Researcher researcher;
    private final Writer writer;
    private final Reviewer reviewer;
    private final ObjectMapper om = new ObjectMapper();

    public String produceArticle(String topic) throws Exception {
        // ① 研究
        log.info("📚 Researcher 开工...");
        Researcher.Research r = researcher.research(topic);
        log.info("Researcher 找到 {} 条事实", r.facts().size());

        // ② 写稿
        log.info("✍️ Writer 开工...");
        String draft = writer.write(om.writeValueAsString(r));

        // ③ 审稿（最多 3 轮）
        for (int round = 1; round <= 3; round++) {
            log.info("🔍 Reviewer 第 {} 轮审查...", round);
            Reviewer.ReviewResult result = reviewer.review(draft);
            log.info("Score: {}, Pass: {}, Feedback: {}",
                    result.score(), result.pass(), result.feedback());

            if (result.pass() && result.score() >= 8) {
                return draft;
            }

            // 反馈给 writer 重写
            String prompt = """
                    原稿：
                    %s

                    Reviewer 反馈：
                    %s

                    请根据反馈重写。
                    """.formatted(draft, result.feedback());
            draft = writer.write(prompt);
        }

        return draft;     // 达到最大轮数，返回当前稿子
    }
}
```

### 2.4 用起来

```bash
curl -X POST "http://localhost:8080/article?topic=量子计算的现状"
```

控制台日志：

```
📚 Researcher 开工...
Researcher 找到 8 条事实
✍️ Writer 开工...
🔍 Reviewer 第 1 轮审查...
Score: 6, Pass: false, Feedback: "缺乏具体数字，第三段过于抽象"
🔍 Reviewer 第 2 轮审查...
Score: 9, Pass: true, Feedback: "整体优秀"
```

> 🎯 **跑出这段日志 = 真正的 Multi-Agent**。

---

## 3. Multi-Agent 的工程取舍（10 分钟）

| 维度 | 单 Agent | Multi-Agent |
|------|---------|------------|
| 复杂度 | 低 | **高** |
| Token 消耗 | 中 | **高（每 Agent 一次调用）**|
| 延迟 | 低 | **高（串行）**|
| 角色专业度 | 一般 | **高** |
| 调试 | 难 | **易（按角色看日志）**|
| 适合场景 | 简单任务 | **复杂创作 / 评审 / 多视角任务** |

---

## 4. 几种 Multi-Agent 拓扑（10 分钟）

```
1. 顺序（Sequential）⭐
   A → B → C → D
   适合：流水线（研究→写作→审查）

2. 主从（Supervisor-Worker）
   Manager 派任务给 Worker，汇总结果
   适合：调度类（让经理决定派给谁）

3. 辩论（Debate）
   两个 Agent 互相提反对意见
   适合：决策类（让 AI"自我审视"）

4. 群聊（Group Chat）
   多 Agent 共享对话，自由发言
   适合：脑暴
```

> 🎯 **本周做的是「顺序型」**——最简单、最实用。其他模式简历项目里可作为"亮点"，但工程价值不一定大。

---

## 5. 高频面试题

**Q1：为什么不用一个超级 Agent？**
A：① Prompt 太长易跑偏 ② 不同任务需不同 system prompt ③ 多 Agent 可以并行 ④ 调试更易

**Q2：Multi-Agent 的代价是什么？**
A：Token 翻倍 + 延迟翻倍 + 实现复杂——必须看场景值不值。

**Q3：怎么避免 Agent 互相吵架？**
A：Orchestrator 是中央调度，角色之间不直接通信；用结构化结果（JSON）传递，避免"对话噪声"。

**Q4：Reviewer 永远说不通过怎么办？**
A：最大轮数限制（如 3 轮），超过则采用当前最高分版本。

---

## 6. 检查清单

- [ ] 实现 §2 的三角色协作 demo
- [ ] 日志能清楚看到"3 个角色串行"
- [ ] Reviewer 提出反馈 → Writer 真的改了
- [ ] 解释 4 种 Multi-Agent 拓扑各适合什么
- [ ] 列出 Multi-Agent 的 3 个工程代价

完成了 ➡️ [Day 4 · MCP 协议](./Day4-MCP协议.md)

---

## 🔗 相关链接

- ⬅️ [Day 2 · Plan-and-Execute](./Day2-Plan-and-Execute.md)
- ➡️ [Day 4 · MCP 协议](./Day4-MCP协议.md)
- ⬆️ [Week 2 总览](./README.md)
- 📚 [Microsoft AutoGen（Multi-Agent 框架，可选阅读）](https://github.com/microsoft/autogen)
