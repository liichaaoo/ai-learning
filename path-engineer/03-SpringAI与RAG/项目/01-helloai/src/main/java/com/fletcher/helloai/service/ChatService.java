package com.fletcher.helloai.service;

import com.fletcher.helloai.dto.Recipe;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.memory.MessageWindowChatMemory;
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

    private final ChatClient chatClient;
    private final ChatClient chatClientWithMemory;

    @Value("classpath:/prompts/customer-service.st")
    private Resource customerServiceTemplate;

    public ChatService(ChatClient.Builder builder) {
        // 普通 chatClient
        this.chatClient = builder.build();

        // 带记忆的 chatClient：MessageWindowChatMemory 默认保留最近 20 条
        ChatMemory memory = MessageWindowChatMemory.builder()
                .maxMessages(20)
                .build();

        this.chatClientWithMemory = builder
                .defaultAdvisors(
                        MessageChatMemoryAdvisor.builder(memory).build()
                )
                .build();
    }

    // ============ 1. 同步对话 ============
    public String chat(String question) {
        return chatClient
                .prompt()
                .user(question)
                .call()
                .content();
    }

    // ============ 2. 流式对话 ============
    public Flux<String> chatStream(String question) {
        return chatClient
                .prompt()
                .user(question)
                .stream()
                .content();
    }

    // ============ 3. 专家模式（System Prompt）============
    public String chatAsExpert(String question) {
        return chatClient
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
        return chatClient
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
        return chatClient
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
}
