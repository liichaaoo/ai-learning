# Day 1 · 环境准备 + API Key 申请

> ⏱️ 目标时间：1-1.5 小时
> 🎯 产出：**能在终端敲 `curl` 调通一次通义千问 API**

---

## 🧭 今天要做 3 件事

```
1. 装好 JDK 17+ 和 IntelliJ IDEA         (15 min)
2. 申请阿里通义千问 API Key                (15 min)
3. 用 curl 调通一次，验证"API 能响应"       (15 min)
```

明天就可以开始写 Spring AI 代码了。

---

## 一、环境检查

### 1.1 JDK 17+

Spring AI 1.0 要求 JDK 17+（最低）。检查：

```bash
java -version
```

输出应该类似：
```
openjdk version "17.0.9" 2023-10-17
OpenJDK Runtime Environment ...
```

**如果你的 JDK 是 8 或 11**：
- macOS：`brew install openjdk@17`
- 或者从 [Azul Zulu](https://www.azul.com/downloads/?package=jdk) 下载

> 💡 推荐装 JDK 21（最新 LTS），更有诚意。

---

### 1.2 IntelliJ IDEA

**社区版就够**（https://www.jetbrains.com/idea/download/）。
你是腾讯员工，公司可能有 Ultimate 版本授权，用哪个都行。

**必装插件**（IDE 里 Preferences → Plugins）：
- ✅ Spring Assistant（如果用 Community 版，需要这个插件识别 Spring Boot）
- ✅ Lombok（省 getter/setter）

---

### 1.3 Maven

```bash
mvn -version
```

如果没有，`brew install maven` 即可。

---

## 二、申请通义千问 API Key（推荐）⭐

### 为什么推荐通义千问

| 模型 | 免费额度 | 开通难度 | 中文效果 |
|------|---------|---------|---------|
| **阿里通义千问** ⭐ | 100 万 Token 免费 | 国内注册，秒开 | 国产最强之一 |
| OpenAI (GPT-4o) | 需充值 $5 起 | 需海外手机号 | 英文最强 |
| Claude | 需充值 | 海外 | 英文超强 |
| 本地 Ollama | 免费无限 | 本地部署 | 一般 |

**对学习而言，通义千问 = 最佳起点**。后面熟练了再配 OpenAI。

---

### 申请步骤（5 分钟）

#### Step 1：登录阿里云

访问 [https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)
（用你的阿里云账号，没有就免费注册）

#### Step 2：开通"百炼大模型服务"

首页会提示"开通服务"，点开通（免费）。

#### Step 3：创建 API-KEY

左侧菜单找到 **"API-KEY"** 或 **"模型调用"** → 创建新的 API-KEY。

会生成一串字符串：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**立刻复制保存到安全的地方**（退出页面就看不到完整 Key 了）。

#### Step 4：记下 Base URL

通义千问的兼容 OpenAI 协议的 Base URL：
```
https://dashscope.aliyuncs.com/compatible-mode/v1
```

**为什么叫"兼容 OpenAI 协议"？** 因为阿里把通义千问做成和 OpenAI 一模一样的接口格式。
- 你写代码时，就**当成调 OpenAI**
- 只是换了 Base URL 和 API Key
- **Spring AI 直接用 OpenAI 客户端就能调通义**（下一步演示）

---

## 三、用 curl 测试 API 是否能调通（关键验证）

### 3.1 设环境变量（临时）

```bash
export DASHSCOPE_API_KEY="sk-你的真实key"
```

### 3.2 发请求

复制下面整段，粘贴进终端回车：

```bash
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-turbo",
    "messages": [
      {"role": "user", "content": "用一句话介绍你自己"}
    ]
  }'
```

### 3.3 预期返回

```json
{
  "id": "chatcmpl-xxxxx",
  "object": "chat.completion",
  "created": 1715505678,
  "model": "qwen-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "我是通义千问，阿里云研发的大语言模型助手，可以回答问题、创作文字..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 12, "completion_tokens": 35, "total_tokens": 47 }
}
```

**看到 `content` 字段里有回复 = 你已经完成了第一次"调用 LLM" ✅**

---

## 四、常见报错处理

### ❌ 401 Unauthorized
- API Key 错了或者环境变量没导入
- 重新检查 `echo $DASHSCOPE_API_KEY` 是不是有值

### ❌ 403 Forbidden
- 百炼服务未开通 → 回去阿里云控制台开通

### ❌ curl: (6) Could not resolve host
- 网络不通，检查 DNS 或代理设置

### ❌ 账户没额度
- 新用户自动有 100 万 Token 免费额度
- 如果显示没额度，去控制台看"资源包"或联系客服

---

## 五、顺便：OpenAI API Key（可选，有条件再申请）

如果你能科学上网 + 有信用卡：

1. 访问 [https://platform.openai.com/](https://platform.openai.com/)
2. 充值 $5（最低）
3. 创建 API Key

但**本周不用 OpenAI 也能学完**，不要因为这个卡住。

---

## 六、把 Key 存成环境变量（永久）⭐

每次都 `export` 太烦，写进 shell 配置：

```bash
# macOS 默认 zsh
echo 'export DASHSCOPE_API_KEY="sk-你的真实key"' >> ~/.zshrc
source ~/.zshrc

# 或 bash
echo 'export DASHSCOPE_API_KEY="sk-你的真实key"' >> ~/.bashrc
source ~/.bashrc
```

验证：

```bash
echo $DASHSCOPE_API_KEY  # 应该输出你的 key
```

---

## 七、⚠️ 安全提醒（必读）

### 1. API Key 永远不要提交到 Git！

```
❌ application.yml 里写死 key
❌ git commit 带 key 的文件
❌ 代码里硬编码 key
```

✅ 正确做法：
- 用环境变量
- 或者 `application.yml` 里写 `${DASHSCOPE_API_KEY}`（占位符）
- `.gitignore` 包含所有可能含 Key 的文件

### 2. 如果 Key 泄露了怎么办

- 立刻去控制台**删除并重新创建**
- 设置用量限额（阿里云有这个功能）

---

## ✍️ 本日"练习"

今天的"练习" = **完成准备工作**：

```
[ ] JDK 17+ 已装
[ ] IntelliJ IDEA 已装
[ ] Maven 已装
[ ] 通义千问 API Key 申请成功
[ ] 用 curl 调通了一次 API（看到返回内容）
[ ] API Key 已设成环境变量
```

**全部勾完** → 明天可以开始写代码。

---

## 🎯 今日收官清单

- [ ] 我能 `java -version` 看到 JDK 17+
- [ ] 我有一个可用的通义千问 API Key
- [ ] 我用 curl 调通了一次 `/chat/completions`
- [ ] 我理解"通义千问兼容 OpenAI 协议"是什么意思
- [ ] 我的 Key 存在环境变量里，而不是代码里
- [ ] 我知道 API Key 泄露的风险和补救措施

---

## 💡 Bonus：今天已经学到的"底层"

用 curl 发一次请求，其实你已经理解了：

- **LLM API 本质**：HTTP POST + JSON
- **messages 格式**：`[{role, content}, ...]`（role 是 system/user/assistant）
- **Token 计费**：返回里有 `usage` 字段

**这些明天就会反复用到**，今天先建立感性认识。

---

## 🔖 下一步

明天 → [Day 2：Hello World](./Day2-HelloWorld.md)（写第一个 Spring AI 程序）
