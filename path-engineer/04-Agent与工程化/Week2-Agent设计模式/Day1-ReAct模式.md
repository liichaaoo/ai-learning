# Day 1 · ReAct 模式（Reasoning + Acting）⭐

> ⏱️ 时间：1.5 小时
> 🎯 目标：理解 ReAct 三段论 + 手撕一个 ReAct 循环

---

## 0. 心法（5 分钟）

> **ReAct = "想一步，做一步，看一眼，再想一步"——人类解决问题的自然方式。**

每一步：

```
Thought    （想）：我接下来要干什么
Action     （做）：调用某个工具，参数是什么
Observation（看）：工具返回了什么
   ↓
   下一轮 Thought（看了结果再想）
```

直到 LLM 觉得"已经够了"，输出最终答案。

---

## 1. 一图速记：ReAct 循环（10 分钟）

```
                          用户问题
                              │
                              ▼
       ┌──────────────────────────────────────────┐
       │                                          │
       │   Thought: 用户问北京天气 + 是否散步        │
       │   Action:  weatherTool("北京")            │
       │                                          │
       └──────────────┬───────────────────────────┘
                      │
                      ▼  Observation: "北京 18°C 晴"
                      │
       ┌──────────────────────────────────────────┐
       │                                          │
       │   Thought: 18°C 晴天对散步很友好           │
       │   Action:  无需更多工具，可以回答          │
       │                                          │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
              最终答案给用户
```

---

## 2. 跟 CoT 的区别（10 分钟）

| 维度 | CoT（Chain-of-Thought）| ReAct |
|------|----------------------|--------|
| 思考方式 | 一口气把整个推理写完 | **想一步停一步，看了结果再想**|
| 能不能调工具 | 不能 | **能** |
| 适合场景 | 数学题、纯推理 | **需要外部信息的任务** |
| 失败兜底 | 全错从头来 | 一步错可以纠正 |

> 🎯 **一句话**：CoT 是"独白"，ReAct 是"对话"——跟工具的对话。

---

## 3. 不用框架，手撕一个 ReAct（30 分钟）⭐

> 写一遍 = 真懂。

### 3.1 Prompt 模板

```java
private static final String REACT_PROMPT = """
        你正在通过 ReAct 模式回答问题。可用工具：
        - weather(city): 查询天气
        - calculator(expr): 计算表达式

        你必须严格按以下格式输出（每轮只输出一段）：

        Thought: <你的思考>
        Action: <工具名>(<JSON 参数>)

        当工具返回结果后，会在下一轮以 Observation: <结果> 形式给你。

        如果你认为可以直接回答，输出：
        Thought: <最终思考>
        Final Answer: <答案>

        问题：%s
        """;
```

### 3.2 主循环

```java
@Service
@RequiredArgsConstructor
public class ManualReActAgent {

    private final ChatLanguageModel model;
    private final Map<String, ToolFunc> tools;     // name -> 工具实现

    public String run(String question) {
        List<ChatMessage> history = new ArrayList<>();
        history.add(SystemMessage.from(REACT_PROMPT.formatted(question)));

        int maxSteps = 10;                          // 防死循环
        for (int step = 0; step < maxSteps; step++) {
            // 1. LLM 输出
            String out = model.generate(history).content().text();
            history.add(AiMessage.from(out));
            System.out.println("─── Step " + step + " ───\n" + out);

            // 2. 是不是终止？
            if (out.contains("Final Answer:")) {
                return out.substring(out.indexOf("Final Answer:") + 13).trim();
            }

            // 3. 解析 Action
            String[] action = parseAction(out);     // [toolName, jsonArgs]
            if (action == null) {
                return "解析失败：\n" + out;
            }

            // 4. 调工具
            ToolFunc tool = tools.get(action[0]);
            String observation;
            try {
                observation = tool.invoke(action[1]);
            } catch (Exception e) {
                observation = "工具异常：" + e.getMessage();
            }

            // 5. 把 Observation 塞回去
            history.add(UserMessage.from("Observation: " + observation));
        }
        return "超出最大步数（可能死循环）";
    }

    private String[] parseAction(String out) {
        // 简化版：用正则把 Action: tool(args) 拎出来
        Pattern p = Pattern.compile("Action:\\s*(\\w+)\\((.*)\\)");
        Matcher m = p.matcher(out);
        if (m.find()) return new String[]{m.group(1), m.group(2)};
        return null;
    }

    public interface ToolFunc {
        String invoke(String jsonArgs);
    }
}
```

### 3.3 注册工具

```java
@Configuration
public class ToolsConfig {
    @Bean
    public Map<String, ManualReActAgent.ToolFunc> tools() {
        return Map.of(
            "weather", args -> "北京 18°C 晴",
            "calculator", args -> {
                // 解析 JSON：{"expr": "1+1"}
                JsonNode n = new ObjectMapper().readTree(args);
                return String.valueOf(eval(n.get("expr").asText()));
            }
        );
    }
}
```

### 3.4 跑一下

```java
String answer = agent.run("北京天气怎么样？合不合适散步？");
```

控制台输出（举例）：

```
─── Step 0 ───
Thought: 我需要先查询北京的天气
Action: weather({"city": "北京"})

─── Step 1 ───
Thought: 北京 18°C 晴天，温度适宜，天气好，适合散步
Final Answer: 北京当前 18°C 晴天，非常适合散步！
```

> 🎯 **跑通这段 = 你真懂 ReAct**。再去看 LangChain4j 的内置实现，会觉得"哦原来就是这玩意"。

---

## 4. LangChain4j 的"内置 ReAct"（10 分钟）

LangChain4j 没有显式的 `ReActAgent` 类——**它把 ReAct 隐藏在了 AiServices + tools 里**。

```java
interface Assistant {
    @SystemMessage("你可以使用工具来回答问题。")
    String chat(@UserMessage String msg);
}

Assistant a = AiServices.builder(Assistant.class)
        .chatLanguageModel(model)
        .tools(new WeatherTool(), new CalcTool())
        .build();

a.chat("北京天气合不合适散步？");
// 内部就是 ReAct 循环：调工具 → 拿结果 → 接着想
```

**LangChain4j 用的是 Function Calling 接口**（OpenAI 的 tool_calls 格式），不是手写文本协议。**但本质还是 ReAct**。

### 两种实现对比

| 维度 | 手写 ReAct（§3）| LangChain4j Tools |
|------|---------------|-------------------|
| 协议 | 文本格式（Thought/Action）| OpenAI tool_calls JSON |
| 兼容性 | 任何 LLM 都行 | 需要模型支持 Function Calling |
| 稳定性 | 容易解析失败 | **稳** |
| 调试 | 看 prompt 简单 | 黑盒一些 |

> 🎯 **生产用 LangChain4j 内置**（稳）；**学习手写一遍**（懂）。

---

## 5. 避免死循环的 4 招（10 分钟）

```
① 硬上限：maxSteps（如 10 步）
② 重复检测：连续 2 次调同工具同参数 → 强制结束
③ Prompt 约束："如果你已有足够信息，请直接输出 Final Answer"
④ 监控指标：tool_call_count > threshold 时告警
```

代码：

```java
Set<String> seen = new HashSet<>();
for (int step = 0; step < maxSteps; step++) {
    // ...
    String sig = action[0] + ":" + action[1];
    if (!seen.add(sig)) {
        return "检测到重复工具调用，可能陷入循环。";
    }
}
```

---

## 6. 检查清单

- [ ] 默写 ReAct 三段论：Thought / Action / Observation
- [ ] 解释 ReAct vs CoT
- [ ] 跑通 §3 手写 ReAct（必做）
- [ ] 跑通 §4 LangChain4j 内置版
- [ ] 知道死循环的 4 种防御
- [ ] 解释为什么生产用 Function Calling（JSON）而不是 ReAct 文本协议

完成了 ➡️ [Day 2 · Plan-and-Execute](./Day2-Plan-and-Execute.md)

---

## 🔗 相关链接

- ⬆️ [Week 2 总览](./README.md)
- ➡️ [Day 2 · Plan-and-Execute](./Day2-Plan-and-Execute.md)
- 📚 [ReAct 论文](https://arxiv.org/abs/2210.03629)
