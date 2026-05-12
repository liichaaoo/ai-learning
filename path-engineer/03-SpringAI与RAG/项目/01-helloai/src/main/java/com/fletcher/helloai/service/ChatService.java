package com.fletcher.helloai.service;

import com.fletcher.helloai.dto.Recipe;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.InMemoryChatMemory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

import static org.springframework.ai.chat.client.advisor.AbstractChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY;

/**
 * 聊天核心逻辑 —— Week 1 毕业示例
 *
 * 演示了 5 种 Spring AI 用法：
 *   1. 同步对话
 *   2. 流式对话
 *   3. System Prompt 专家模式
 *   4. Prompt 模板（.st 文件 + 变量注入）
 *   5. 结构化输出（.entity(Class)）
 *   6. 多轮记忆（ChatMemory + Advisor）
 */
@Service
public class ChatService {

    private final ChatClient chatClient;
    private final ChatClient chatClientWithMemory;

    @Value("classpath:/prompts/customer-service.st")
    private Resource customerServiceTemplate;

    public ChatService(ChatClient.Builder builder) {
        // 普通 chatClient
        this.chatClient = builder.build();

        // 带记忆的 chatClient
        InMemoryChatMemory memory = new InMemoryChatMemory();
        this.chatClientWithMemory = ChatClient.builder(builder.build().prompt().toString() != null
                ? null : null)  // placeholder，实际用下面的注入方式
                .build();
        // 注：Spring AI 1.x 版本可能是下面这种写法：
        //   .defaultAdvisors(new MessageChatMemoryAdvisor(memory))
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

    // ============ 6. 多轮记忆（可选，Spring AI 具体 API 以版本为准）============
    /* 伪代码示意（不同 Spring AI 版本 API 略有差异）：

    public String chatWithMemory(String conversationId, String question) {
        return chatClientWithMemory
                .prompt()
                .user(question)
                .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, conversationId))
                .call()
                .content();
    }
    */
}
