package com.fletcher.helloai.service;

import com.fletcher.helloai.dto.Recipe;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

/**
 * 聊天核心逻辑 —— Week 1 毕业示例
 *
 * 演示了 6 种 Spring AI 用法：
 *   1. 同步对话
 *   2. 流式对话
 *   3. System Prompt 专家模式
 *   4. Prompt 模板（.st 文件 + 变量注入）
 *   5. 结构化输出（.entity(Class)）
 *   6. 多轮记忆（ChatMemory + Advisor）
 * 注：使用 Spring AI 1.0.0 GA。
 *   - InMemoryChatMemory 已被移除，统一用 ChatMemory 接口
 *   - 默认实现 MessageWindowChatMemory（按消息条数滑窗）
 *   - MessageChatMemoryAdvisor 改为 builder 模式
 */
@Service
public class ChatService {

    /** 多轮对话时用来区分会话的 key（Spring AI 1.0 起约定为 "chat_memory_conversation_id"） */
    public static final String CONVERSATION_ID_KEY = ChatMemory.CONVERSATION_ID;

    private final ChatClient deepseekClient;
    private final ChatClient ollamaClient;
    private final ChatClient qwenClient;
    private final TimeTool timeTool;
    private final OrderTool orderTool;
    private final ChatClient chatClientWithMemory;

    @Value("classpath:/prompts/customer-service.st")
    private Resource customerServiceTemplate;

    public ChatService(@Qualifier("qwenClient") ChatClient qwenClient,
                       @Qualifier("ollamaClient") ChatClient ollamaClient,
                       @Qualifier("deepseekClient") ChatClient deepseekClient,
                       TimeTool timeTool, OrderTool orderTool) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
        this.deepseekClient = deepseekClient;
        this.timeTool = timeTool;
        this.orderTool = orderTool;

        // ⚠️ 注意：ChatClient.Builder 是有状态对象，Spring 注入的是共享实例。
        // 如果在同一个 builder 上先 build()，再 defaultAdvisors(memory)，再 build()，
        // 由于 build() 不是深拷贝快照，第二次添加的 advisor 会"反向"影响第一次 build 出的
        // 普通 chatClient —— 表现就是：调用普通 /chat/stream 接口，LLM 居然也有记忆。
        //
        // 正确做法：先 build() 普通版，再用 chatClient.mutate() 派生一个带 memory 的副本，
        // mutate() 会基于现有配置克隆出一个全新的 builder，互不影响。

        // 1) 普通 chatClient（无 memory）

        // 2) 带记忆的 chatClient：MessageWindowChatMemory 默认保留最近 20 条
        ChatMemory memory = MessageWindowChatMemory.builder()
                .maxMessages(20)
                .build();

        this.chatClientWithMemory = this.qwenClient.mutate()
                .defaultAdvisors(MessageChatMemoryAdvisor.builder(memory).build())
                .build();
    }

    // ============ 1. 同步对话 ============
    public String chat(String question) {
        return qwenClient
                .prompt()
                .user(question)
                .call()
                .content();
    }

    // ============ 2. 流式对话 ============
    public Flux<String> chatStream(String question) {
        return qwenClient
                .prompt()
                .user(question)
                .stream()
                .content();
    }

    public Flux<String> deepseekChatStream(String question) {
        return deepseekClient
                .prompt()
                .user(question)
                .stream()
                .content();
    }

    // ============ 3. 专家模式（System Prompt）============
    public String chatAsExpert(String question) {
        return qwenClient
                .prompt()
                .system("""
                        你是一位资深 Java 架构师，有 15 年工作经验。
                        回答问题必须：
                        1) 给出明确结论（不能说"看情况"）；
                        2) 说清楚理由（列出 2-3 条）；
                        3) 总字数不超过 200 字。
                        """)
                .user(question)
                .call()
                .content();
    }

    // ============ 4. Prompt 模板（变量注入）============
    public String industryCustomerService(String industry, String question) {
        return qwenClient
                .prompt()
                .system(spec -> spec
                        .text(customerServiceTemplate)
                        .param("industry", industry)
                )
                .user(question)
                .call()
                .content();
    }

    // ============ 5. 结构化输出（⭐ Week 1 Day 5 核心）============
    public Recipe generateRecipe(String dishName) {
        return qwenClient
                .prompt()
                .system("你是一位专业厨师。我会告诉你一道菜，你返回标准的菜谱信息。")
                .user("我想做一道 " + dishName + "，请给出完整菜谱。")
                .call()
                .entity(Recipe.class);
    }

    // ============ 6. 多轮记忆（同一个 conversationId 内 LLM 能记住上下文）============
    public String chatWithMemory(String conversationId, String question) {
        return chatClientWithMemory
                .prompt()
                .user(question)
                .advisors(a -> a.param(CONVERSATION_ID_KEY, conversationId))
                .call()
                .content();
    }

    public Flux<String> chatStreamWithMemory(String conversationId, String question) {
        return chatClientWithMemory
                .prompt()
                .user(question)
                .advisors(a -> a.param(CONVERSATION_ID_KEY, conversationId))
                .stream()
                .content();
    }

    public String chatWithTools(String q) {
        return qwenClient.prompt().tools(timeTool, orderTool).system("""
                你是一位工具调用专家，用户会给出一个任务，你必须使用工具完成任务。如果没有合适的工具，你必须拒绝任务。
                """).user(q).call().content();
    }


    // 云端（便宜）
    public String chatCheap(String q) {
        return qwenClient.prompt().user(q).call().content();
    }

    // 本地（免费 + 私有）
    public String chatLocal(String q) {
        return ollamaClient.prompt().user(q).call().content();
    }

    // 云端 + 工具
    public String chatCheapWithTools(String q) {
        return qwenClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }

    // 本地 + 工具（注意：并非所有本地小模型都支持 Function Calling）
    public String chatLocalWithTools(String q) {
        return ollamaClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }
}
