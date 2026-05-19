# Spring AI 多模态 · 面试够用版

> 🎯 **定位**：本笔记不是教你做多模态项目，是让你**会聊不会做**——花 1-2 小时读完，面试官问起来能讲 5 分钟。
>
> 📌 **前置判断**：见 [`./SpringAI入门.md`](./SpringAI入门.md)。如果你的目标项目是企业 RAG 知识库（Week5-6），多模态**不在主线**，但要知道它存在、知道为什么没做、知道要做该怎么做。

---

## 一、Spring AI 多模态全景图（2 分钟搞清边界）

Spring AI 1.0 的多模态能力分成 **4 个独立的模型抽象**，互相不耦合：

| 抽象 | 干什么 | 典型实现 | 企业落地频率 |
|------|--------|---------|------------|
| **ChatModel + Media**（Vision） | **图 → 文字理解**（看图说话、看图问答） | GPT-4o / Claude 3.5 / Qwen-VL | ⭐⭐⭐⭐ 最常用 |
| **ImageModel** | **文字 → 图**（文生图） | DALL·E 3 / Stable Diffusion / 通义万相 | ⭐⭐ 营销/电商场景 |
| **AudioTranscriptionModel** | **音 → 文字**（语音识别） | Whisper / 阿里 Paraformer | ⭐⭐⭐ 会议/客服 |
| **TextToSpeechModel**（TTS） | **文字 → 音**（语音合成） | OpenAI TTS / 阿里 CosyVoice | ⭐⭐ 数字人/无障碍 |

> 💡 **关键认知**：所谓"多模态"在工程上其实是 4 件事，不是 1 件事。面试时别笼统说"我懂多模态"，要按场景拆开讲。

---

## 二、Vision（图文输入）—— 唯一必须会的那一个

90% 的"多模态需求"实际只需要 Vision 一个能力。代码极简：

### 1. 最小例子：传一张图问问题

```java
@RestController
public class VisionController {

    private final ChatClient chatClient;

    public VisionController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    @PostMapping("/vision")
    public String describe(@RequestParam("file") MultipartFile file,
                           @RequestParam String question) throws IOException {

        // 关键：用 Media 把图片塞进 user message
        Media image = new Media(
            MimeTypeUtils.IMAGE_PNG,
            new ByteArrayResource(file.getBytes())
        );

        return chatClient.prompt()
            .user(u -> u.text(question).media(image))   // 文字 + 图片同时传
            .call()
            .content();
    }
}
```

### 2. 配置（用支持 Vision 的模型）

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o          # ⭐ 必须用支持 vision 的模型
          # 或 gpt-4o-mini（便宜 6 倍，精度够用）
```

国产替代：

| 模型 | 谁家 | 价格相对 GPT-4o |
|------|------|---------------|
| `qwen-vl-max` | 阿里 | ~1/3 |
| `qwen-vl-plus` | 阿里 | ~1/10 |
| `glm-4v` | 智谱 | ~1/5 |

### 3. 也能传 URL（不一定要上传二进制）

```java
Media image = new Media(MimeTypeUtils.IMAGE_PNG,
        new URI("https://example.com/architecture.png").toURL());
```

### 4. 多张图一起传

```java
chatClient.prompt()
    .user(u -> u.text("对比这两张架构图的差异")
                .media(img1)
                .media(img2))
    .call()
    .content();
```

---

## 三、其他三个能力 · 知道有就行

### 1. ImageModel（文生图）

```java
@Autowired private ImageModel imageModel;

ImageResponse resp = imageModel.call(new ImagePrompt(
    "一只戴墨镜的橘猫在写 Java 代码，赛博朋克风格"
));
String url = resp.getResult().getOutput().getUrl();
```

**企业用得少**，主要是营销素材生成、电商主图、运营图。一般直接调通义万相 / Midjourney API，**不一定要走 Spring AI**。

### 2. AudioTranscriptionModel（语音转文字）

```java
@Autowired private OpenAiAudioTranscriptionModel transcriptionModel;

Resource audio = new FileSystemResource("/path/meeting.mp3");
String text = transcriptionModel.call(new AudioTranscriptionPrompt(audio))
        .getResult().getOutput();
```

**典型场景**：会议纪要、客服录音质检、播客转录。

> ⭐ **最有价值的组合**：Whisper 转文字 → 灌进 RAG → 做"会议纪要语义检索"。这个能直接进简历。

### 3. TextToSpeechModel（TTS）

```java
SpeechResponse resp = speechModel.call(new SpeechPrompt("你好世界"));
byte[] audio = resp.getResult().getOutput();
// 写文件 / 流给前端播放
```

**企业用得少**，多是无障碍、数字人、车载语音。

---

## 四、企业级落地的真实选型（最容易被问的点）

### 场景：带图的 PDF 想做 RAG，怎么选？

| 路线 | 怎么做 | 成本（1 万页） | 可控性 | 适用 |
|------|-------|------------|-------|------|
| **A. OCR 抽文** | PaddleOCR / 腾讯云 OCR → 文本 → 切分 → Embedding | **¥10-50** | 高（能精确分片+引用页码） | ⭐ **企业 RAG 主流** |
| **B. Vision 抽文** | GPT-4o 看每页 → 总结成文本 → 切分 → Embedding | **¥500-2000** | 中（抽出来的内容 token 计费贵） | 表格/图表多的财报 |
| **C. 多模态 Embedding** | CLIP / 通义多模态向量 → 多模态向量库 | **更贵+难落地** | 低（向量库选项少、检索精度不稳） | 前沿研究 |

> ✅ **标准答案**：99% 选 A，复杂表格/图表场景选 A + B 混合（普通页 OCR、含表页 Vision）。

### 场景：用户在客服里发了一张报错截图

```
图片 ──► Vision 模型抽文字 + 错误描述 ──► 进 RAG 检索知识库 ──► 流式回答
```

代码上就是把上面 Vision 那段当成 RAG 检索前的"问题改写"步骤。

### 场景：图片量很大、调用很频繁

**永远先想 OCR 不行的话再上 Vision**。Vision 调用单价是文本的 5-20 倍，每张图按图片分辨率额外算 token：

```
GPT-4o 一张 1024×1024 图 ≈ 765 输入 token ≈ $0.002
1 万张 = $20，10 万张 = $200
```

---

## 五、避坑指南

### ⚠️ 坑 1：模型选错，调用直接报 400

`gpt-4` / `gpt-3.5-turbo` 不支持 vision，必须用 `gpt-4o` / `gpt-4o-mini` / `gpt-4-turbo`。

### ⚠️ 坑 2：图太大，超 token / 超 size 限制

OpenAI 单图 ≤ 20MB，**且超过 2048×2048 会被自动缩放**。建议上传前自己 resize 到 1024 长边以内：
- 省 token（成本降一半）
- 速度更快
- 精度损失基本看不出

```java
BufferedImage resized = Thumbnails.of(originalImage)
        .size(1024, 1024)
        .asBufferedImage();
```

### ⚠️ 坑 3：把 Base64 字符串直接塞 Media，性能爆炸

`Media` 接受 `Resource`，**不要先转 Base64 再 new String 再塞进去**——大图会让 JVM 内存抖动。直接用 `ByteArrayResource` 或 `FileSystemResource`。

### ⚠️ 坑 4：流式 + Vision 同时用要确认模型支持

GPT-4o 支持 vision + stream 同时；但有些国产 vision 模型只支持非流式。报错形如 `stream not supported with image input` 时换模型或降级为非流式。

### ⚠️ 坑 5：Whisper 转录长音频前必须切片

OpenAI Whisper API 单次 ≤ 25MB（约 25 分钟）。长会议必须先 ffmpeg 切成 10 分钟一片，转完拼接：

```bash
ffmpeg -i meeting.mp3 -f segment -segment_time 600 -c copy out_%03d.mp3
```

### ⚠️ 坑 6：多模态成本失控

强烈建议在 `ChatClient` 上加一个 Advisor 拦截 vision 请求做配额控制，**别让前端能自由上传图片调 GPT-4o**。

---

## 六、面试可能问的 5 个问题 + 标准答案

### Q1：你的 RAG 项目有支持图片吗？为什么？

> 没有原生支持图片，因为我们的文档以文本和带图 PDF 为主。带图 PDF 的图片信息**走 OCR 抽文路线**进 RAG，没有上 Vision 模型。原因有三：（1）Vision 单次调用成本是文本的 5-10 倍；（2）OCR 抽出的文字能精确做分片和页码引用，Vision 抽出的总结无法对应原文位置；（3）我们文档里的图主要是架构图和截图，OCR + alt-text 已经够。如果是金融财报这种表格密集场景，会考虑混合方案。

### Q2：Spring AI 怎么传图给模型？

> 用 `Media` 类。在 `ChatClient.prompt().user()` 里调 `.media(media)` 把图和文字一起传。`Media` 第一个参数是 MIME type，第二个参数是 `Resource`，可以是 `ByteArrayResource`、`FileSystemResource` 或 URL。底层会按各家模型的协议（OpenAI 是 `image_url` 字段，Anthropic 是 `source.base64`）做适配，业务代码不用关心。

### Q3：OCR 和 Vision 怎么选？

> 三个维度：**成本**（OCR 便宜 50-200 倍）、**可控性**（OCR 能定位原文坐标，Vision 出来的是模型的总结）、**精度**（手写、复杂表格 Vision 强，标准印刷体 OCR 够）。企业 RAG 默认 OCR，特殊页面 Vision 兜底。

### Q4：多模态 Embedding 是什么？为什么大家不用？

> 把图和文映射到同一个向量空间（如 CLIP），实现"用文字搜图"或"用图搜图"。**没大规模落地**的原因：（1）开源多模态向量库少（Milvus 支持但生态不成熟）；（2）多模态向量在中文场景效果不稳；（3）大部分需求用"图 → Vision 抽文 → 文本向量"两步走就够了，没必要上多模态向量。

### Q5：如果让你给 RAG 加多模态，你怎么做？

> 分四步：（1）**入库侧**：PDF 解析时识别图片，重要图片调 Vision 生成 caption（图说），caption 和原文绑定一起切分入库；（2）**检索侧**：用户提问命中带图的 chunk 时，把原图也一起返回；（3）**生成侧**：如果是图片相关的提问（"这张架构图是什么意思"），把图通过 `Media` 一起传给 Vision 模型；（4）**成本控制**：Vision 调用走单独配额，前端图片必须先 resize 到 1024 长边以内。

---

## 七、什么时候你应该真的去学（而不是只"会聊"）

下面这几种情况就别只停留在面试话术，要真做项目：

- 🏥 **目标公司在医疗/金融/工业/电商**：业务天然图多
- 📋 **JD 里写了** "多模态" / "Vision" / "OCR" / "图像理解"
- 💼 **简历想再加一个项目**：可以做"会议纪要 RAG"（Whisper + RAG），ROI 最高
- 🚀 **跳到大模型应用团队**：多模态是基本盘

否则——**先把 Week5-6 的企业 RAG 知识库做扎实**，多模态等真用上再补 1-2 天就够。

---

## 八、推荐资源（按优先级）

1. [Spring AI Multimodal 官方文档](https://docs.spring.io/spring-ai/reference/api/chat/openai-chat.html#_multimodal)（必看，30 分钟）
2. [Spring AI Image Generation](https://docs.spring.io/spring-ai/reference/api/imageclient.html)（10 分钟扫一遍）
3. [Spring AI Audio Transcription](https://docs.spring.io/spring-ai/reference/api/audio/transcriptions.html)（10 分钟扫一遍）
4. [OpenAI Vision Pricing 计算器](https://openai.com/api/pricing/)（实战必查）

---

## 九、一页纸总结

```
┌─────────────────────────────────────────────────────┐
│ Spring AI 多模态 = 4 件事                            │
│   ① Vision      = ChatClient + Media   ⭐ 最常用      │
│   ② 文生图       = ImageModel           企业少用      │
│   ③ 语音转文字   = TranscriptionModel   会议/客服     │
│   ④ TTS         = TextToSpeechModel     数字人        │
│                                                       │
│ 企业 RAG 处理图片：                                    │
│   默认 OCR > Vision > 多模态 Embedding                │
│                                                       │
│ 面试一句话：                                           │
│   "我的项目走 OCR 路线，因为成本和可控性最优；         │
│    Vision 我知道怎么用，留作复杂表格场景的兜底方案。"  │
└─────────────────────────────────────────────────────┘
```

**核心心法**：多模态在企业 AI 应用里是"按需开启的能力"，不是"必备底座"。把主线打透，比浅尝多模态有用 10 倍。
