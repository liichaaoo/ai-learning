package com.fletcher.multitools.service;

import com.fletcher.multitools.tools.OrderTool;
import com.fletcher.multitools.tools.TimeTool;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

/**
 * 基础聊天服务 - 展示 Function Calling + 多模型
 */
@Service
public class ChatService {

    private final ChatClient qwenClient;
    private final ChatClient ollamaClient;
    private final TimeTool timeTool;
    private final OrderTool orderTool;

    public ChatService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            @Qualifier("ollamaClient") ChatClient ollamaClient,
            TimeTool timeTool, OrderTool orderTool) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
        this.timeTool = timeTool;
        this.orderTool = orderTool;
    }

    // ============ 基础 ============
    public String chatCheap(String q) {
        return qwenClient.prompt().user(q).call().content();
    }

    public String chatLocal(String q) {
        return ollamaClient.prompt().user(q).call().content();
    }

    // ============ 带 Function Calling ============
    public String chatCheapWithTools(String q) {
        return qwenClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }

    public String chatLocalWithTools(String q) {
        return ollamaClient.prompt().user(q).tools(timeTool, orderTool).call().content();
    }
}
