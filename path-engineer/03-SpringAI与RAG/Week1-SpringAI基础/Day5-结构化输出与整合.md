# Day 5 · 结构化输出 + 整合 Demo（Week 1 收官）

> ⏱️ 目标时间：2 小时（周末做）
> 🎯 产出：**完整 Hello AI 工程 + 结构化输出能力 + 30 分钟给同事演示**

---

## 🧭 今天的主线

前 4 天分别学了：**环境 → Hello World → 流式 → Prompt**。

**今天做两件事**：

1. **结构化输出**：让 LLM 返回 Java 对象（不只是字符串）
2. **整合成完整 demo**：代码优化、前端完善、写 README

---

## 一、为什么要结构化输出？

### 1.1 痛点：AI 返回自由文本，下游难处理

假设你做"菜谱生成"接口：

```java
String answer = chatClient
    .prompt()
    .user("做一道番茄炒蛋，告诉我食材和步骤")
    .call()
    .content();

// 返回:
// "番茄炒蛋需要以下食材：番茄 2 个，鸡蛋 3 个...
//  步骤：1. 番茄切块；2. 鸡蛋打散..."
```

**问题**：这是一段自由文本。
- 想提取食材列表 → 得写正则
- 想把步骤展示成列表 → 得解析
- 想存数据库 → 全是字符串

### 1.2 解法：让 LLM 返回 JSON，Spring AI 自动映射成 Java 对象

```java
Recipe recipe = chatClient
    .prompt()
    .user("做一道番茄炒蛋")
    .call()
    .entity(Recipe.class);    // ⭐ 直接拿对象！

System.out.println(recipe.name());           // "番茄炒蛋"
System.out.println(recipe.ingredients());    // List<String>
System.out.println(recipe.steps());          // List<String>
```

**这就是 Java 工程师的春天**：不用手工处理 JSON，不用解析字符串，**和访问数据库查对象一样丝滑**。

---

## 二、定义 Recipe DTO

在 `src/main/java/com/fletcher/helloai/dto/` 下新建：

```java
package com.fletcher.helloai.dto;

import java.util.List;

// Java 17+ 的 record（极简 POJO）
public record Recipe(
        String name,               // 菜名
        int difficulty,            // 难度 1-5
        int cookTime,              // 预估耗时（分钟）
        List<String> ingredients,  // 食材
        List<String> steps         // 步骤
) {}
```

**Java 17 `record`** 自动生成 getter/equals/hashCode/toString，比 Lombok 还简洁，写 DTO 首选。

---

## 三、Service 层：加 recipe 方法

在 `ChatService.java` 里新增：

```java
import com.fletcher.helloai.dto.Recipe;

public Recipe generateRecipe(String dishName) {
    return chatClient
        .prompt()
        .system("你是一位专业厨师。我会告诉你一道菜，你返回标准的菜谱信息。")
        .user("我想做一道 " + dishName + "，请给出完整菜谱。")
        .call()
        .entity(Recipe.class);   // ⭐ 魔法发生的地方
}
```

---

## 四、`.entity(Class)` 的原理（你一定好奇）⭐

Spring AI 做的三件事：

### Step 1：自动生成 JSON Schema 要求

在发请求前，Spring AI 分析 `Recipe.class` 的结构，**自动往 Prompt 里塞一段"输出格式要求"**：

```
最终用户原 prompt: "做一道番茄炒蛋"

Spring AI 实际发给 LLM 的是:
"""
做一道番茄炒蛋

请严格按照以下 JSON Schema 返回，不要添加任何解释文字：
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "difficulty": {"type": "integer"},
    "cookTime": {"type": "integer"},
    "ingredients": {"type": "array", "items": {"type": "string"}},
    "steps": {"type": "array", "items": {"type": "string"}}
  }
}
"""
```

### Step 2：LLM 按格式返回

LLM 看到 Schema 后，会吐 JSON 字符串：

```json
{
  "name": "番茄炒蛋",
  "difficulty": 1,
  "cookTime": 10,
  "ingredients": ["番茄 2 个", "鸡蛋 3 个", "盐", "糖"],
  "steps": ["番茄切块", "鸡蛋打散", "..."]
}
```

### Step 3：Jackson 反序列化

Spring AI 调用 Jackson 把 JSON 变成 `Recipe` 对象。

### 💡 对你的意义

**你什么都不用写**（不用写 Schema 描述、不用写 JSON 解析），**就能把 LLM 的输出直接当成 Java 对象用**。

Spring AI 的"Java 化"魔力就在这里。

---

## 五、Controller：新增接口

```java
@PostMapping("/chat/recipe")
public Recipe recipe(@RequestParam String dish) {
    return chatService.generateRecipe(dish);
}
```

测试：
```bash
curl -X POST "http://localhost:8080/chat/recipe?dish=蛋炒饭"
```

返回：
```json
{
  "name": "蛋炒饭",
  "difficulty": 1,
  "cookTime": 15,
  "ingredients": ["米饭 2 碗", "鸡蛋 2 个", "葱花", "盐", "酱油"],
  "steps": [
    "米饭先隔夜冷藏",
    "鸡蛋打散",
    "热锅下油，炒鸡蛋盛出",
    "再次下油，下米饭炒散",
    "加入鸡蛋、葱花调味即可"
  ]
}
```

**前端 / 小程序 / 另一个微服务，拿到这个 JSON 就能直接用。AI 真正融入了你的系统**。

---

## 六、整合前端：完善 index.html

把 Day 3 的 index.html 升级成**多功能演示页**：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hello Spring AI - Demo</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, "PingFang SC", sans-serif;
            max-width: 800px; margin: 40px auto; padding: 20px;
            background: #fafafa;
        }
        h1 { color: #333; }
        .tab { display: inline-block; padding: 8px 16px; cursor: pointer; background: #eee; border-radius: 4px 4px 0 0; }
        .tab.active { background: #fff; font-weight: bold; }
        .panel {
            background: #fff; border-radius: 0 4px 4px 4px; padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        input, textarea, select {
            width: 100%; padding: 10px; margin: 8px 0;
            border: 1px solid #ddd; border-radius: 4px; font-size: 14px;
        }
        button {
            background: #007aff; color: white; padding: 10px 20px;
            border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
        }
        button:hover { background: #0056b3; }
        pre, .output {
            background: #f5f5f7; padding: 16px; border-radius: 4px;
            min-height: 100px; white-space: pre-wrap; word-wrap: break-word;
            font-family: "SF Mono", Monaco, monospace; font-size: 13px;
        }
    </style>
</head>
<body>
    <h1>🤖 Hello Spring AI</h1>

    <!-- Tab 切换 -->
    <div>
        <div class="tab active" onclick="switchTab('stream')">💬 流式对话</div>
        <div class="tab" onclick="switchTab('expert')">🎓 专家模式</div>
        <div class="tab" onclick="switchTab('recipe')">🍳 菜谱生成（结构化）</div>
    </div>

    <div class="panel">
        <!-- 流式对话 -->
        <div id="panel-stream">
            <input id="stream-q" placeholder="问点什么..." value="用一句话介绍自己" />
            <button onclick="doStream()">发送</button>
            <div class="output" id="stream-out"></div>
        </div>

        <!-- 专家模式 -->
        <div id="panel-expert" style="display:none">
            <input id="expert-q" placeholder="问点什么..." value="我该用 MySQL 还是 PostgreSQL？" />
            <button onclick="doExpert()">问资深架构师</button>
            <div class="output" id="expert-out"></div>
        </div>

        <!-- 菜谱生成 -->
        <div id="panel-recipe" style="display:none">
            <input id="recipe-dish" placeholder="想做什么菜..." value="番茄炒蛋" />
            <button onclick="doRecipe()">生成菜谱</button>
            <pre id="recipe-out"></pre>
        </div>
    </div>

    <script>
        function switchTab(name) {
            ['stream', 'expert', 'recipe'].forEach(n => {
                document.getElementById('panel-' + n).style.display = n === name ? 'block' : 'none';
            });
            document.querySelectorAll('.tab').forEach((el, i) => {
                el.classList.toggle('active', el.textContent.toLowerCase().includes(name));
            });
        }

        function doStream() {
            const q = document.getElementById('stream-q').value;
            const out = document.getElementById('stream-out');
            out.textContent = '';
            const src = new EventSource(`/chat/stream?q=${encodeURIComponent(q)}`);
            src.onmessage = e => out.textContent += e.data;
            src.onerror = () => src.close();
        }

        async function doExpert() {
            const q = document.getElementById('expert-q').value;
            const out = document.getElementById('expert-out');
            out.textContent = '思考中...';
            const res = await fetch(`/chat/expert?q=${encodeURIComponent(q)}`);
            out.textContent = await res.text();
        }

        async function doRecipe() {
            const dish = document.getElementById('recipe-dish').value;
            const out = document.getElementById('recipe-out');
            out.textContent = '生成中...';
            const res = await fetch(`/chat/recipe?dish=${encodeURIComponent(dish)}`, {method: 'POST'});
            const json = await res.json();
            out.textContent = JSON.stringify(json, null, 2);
        }
    </script>
</body>
</html>
```

**效果**：打开浏览器就能切换 3 种交互模式，是一个像样的 Demo。

---

## 七、写一份项目 README.md

在 `01-helloai/` 项目根目录下（不是 Week 教程这里）新建 `README.md`：

```markdown
# Hello Spring AI

一个基于 Spring Boot 3 + Spring AI 的最小 AI 应用示例。
用 **通义千问** 作为后端模型（兼容 OpenAI 协议）。

## ✨ 特性

- 🗨️ 同步 / 流式（SSE）两种对话模式
- 🎓 可配置的 System Prompt（专家角色）
- 🍳 结构化输出（LLM 返回 Java 对象）
- 🧠 Prompt 模板 + 多轮记忆（带 conversation id）
- 🎨 简洁的 HTML 测试页

## 🚀 快速开始

### 前置
- JDK 17+
- Maven 3.8+
- 通义千问 API Key（[免费申请](https://dashscope.console.aliyun.com/)）

### 启动
```bash
# 1. 配置 Key
export DASHSCOPE_API_KEY="sk-xxx"

# 2. 编译启动
mvn spring-boot:run

# 3. 打开浏览器
open http://localhost:8080
```

## 📡 API

| 接口 | 功能 | 示例 |
|------|------|------|
| `GET /chat?q=xxx` | 同步对话 | `curl "localhost:8080/chat?q=你好"` |
| `GET /chat/stream?q=xxx` | 流式对话（SSE） | 用浏览器 EventSource |
| `GET /chat/expert?q=xxx` | 资深架构师模式 | 加了 System Prompt |
| `POST /chat/recipe?dish=xxx` | 菜谱生成（结构化）| 返回 JSON |
| `GET /chat/memory?convId=xxx&q=xxx` | 带记忆的多轮对话 | 同 convId 有记忆 |

## 🧱 技术栈

| 组件 | 版本 |
|------|------|
| Spring Boot | 3.3.x |
| Spring AI | 1.0.0 |
| JDK | 17+ |
| 大模型 | 通义千问 qwen-turbo |

## 🗂️ 项目结构

见 `src/` 目录。核心类：
- `ChatController` - HTTP 接口
- `ChatService` - 核心逻辑
- `dto/Recipe` - 结构化输出示例

## 🛡️ 安全

- ✅ API Key 仅通过环境变量注入，绝不硬编码
- ✅ `.gitignore` 排除所有敏感文件
```

---

## 八、一个 `.gitignore` 模板（必做）

在项目根目录 `.gitignore`：

```
# Maven
target/
*.log

# IDEA
.idea/
*.iml

# VS Code
.vscode/

# macOS
.DS_Store

# 敏感
*.env
*.key
application-local.yml   # 本地配置
```

---

## 九、"给面试官演示"的 30 秒脚本

**背下这一段**，以后问到"你做过 Spring AI 项目吗"，立刻能讲：

> 我做了一个 Spring Boot 3 + Spring AI 的最小 AI 应用示例，支持：
>
> 1. **同步和流式对话** —— 流式用 SSE + Flux，首字延迟 < 500ms
> 2. **Prompt 工程** —— System Prompt 切换专家角色，用 `.st` 模板文件动态注入变量
> 3. **结构化输出** —— 通过 `.entity(Recipe.class)` 让 LLM 返回 Java 对象，Spring AI 自动生成 JSON Schema 并反序列化
> 4. **多轮记忆** —— `ChatMemory` + `MessageChatMemoryAdvisor`，支持 conversation id 隔离
>
> 用的模型是通义千问（兼容 OpenAI 协议），部署在本地或腾讯云都可以。代码 200 行左右。

**这段讲完 = 面试官知道你是真的做过**，不是背书。

---

## 十、 Week 1 收官 ✅

### 你现在拥有

```
✅ 一个能跑的 Spring AI 工程（Hello World 级别）
✅ 5 个有用的 API 接口
✅ 前端交互页面
✅ 理解 SSE 流式、Prompt 工程、结构化输出
✅ 一份可以写进简历的项目
```

### 本周出关自测（回顾 Week 1 README 的 5 题）

1. ChatClient vs ChatModel 区别？
2. 同步和流式返回类型？
3. System / User Prompt 作用？
4. Prompt 模板的变量语法？
5. `.entity(Recipe.class)` 的原理？

**4+ 题能答 = Week 1 通过**。

---

## ✍️ 本日实战清单

```
[ ] Recipe record 定义
[ ] ChatService.generateRecipe() 实现
[ ] /chat/recipe 接口
[ ] index.html 升级成 3-tab 演示页
[ ] 项目根目录 README.md 写好
[ ] .gitignore 配好
[ ] 整个工程能完整跑起来
[ ] 用 git 提交到 GitHub（或工蜂）
```

---

## 🎯 Week 1 毕业自我评估

> **打开你的 01-helloai 工程，能回答下面问题 → Week 1 毕业**

1. `.call()` 和 `.stream()` 的返回类型是什么？
2. 为啥要 `produces = TEXT_EVENT_STREAM_VALUE`？
3. `.system(spec -> spec.text().param())` 这段代码做了什么？
4. `.entity(Recipe.class)` 的执行过程？
5. 现在让你给 ChatMemory 换成 Redis 存，思路是什么？

**都能答 = 准备好进入 Week 2（Function Calling + 多模型）**

---

## 🔖 下一步（下周，Week 2）

Week 2 预告：
- **Function Calling**：让 AI 调用你的业务方法（"订会议""查订单"）
- **多模型接入**：一个工程同时接 OpenAI、通义、Claude、Ollama
- **路由策略**：按成本、按场景选模型

这是**让 AI 从"聊天机器人"升级到"能干活的 Agent"** 的关键。

---

## 💌 一段话给未来的自己

> 如果你是 W19 ~ W24 某一周才读到这里的 Fletcher ——
>
> 记得 Week 1 结束时你第一次看到流式文字在浏览器里蹦出来的那个下午吗？
>
> 那是你**从"Java 工程师"到"Java + AI 工程师"**身份转变的起点。
>
> 后面还有 4 周比这更难、更精彩的路。
>
> 别急。按节奏走。产出为王。
