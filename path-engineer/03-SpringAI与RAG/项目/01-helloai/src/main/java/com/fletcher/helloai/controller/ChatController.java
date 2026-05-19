package com.fletcher.helloai.controller;

import com.fletcher.helloai.dto.Recipe;
import com.fletcher.helloai.service.ChatService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

/**
 * 所有 HTTP 接口集中在这里（浏览器访问 / 演示用）
 */
@RestController
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    /**
     * 同步对话
     * 访问: http://localhost:8080/chat?q=你好
     */
    @GetMapping("/chat")
    public String chat(@RequestParam("q") String question) {
        return chatService.chat(question);
    }

    @GetMapping("/chat/agent")
    public String agent(@RequestParam String q) {
        return chatService.chatWithTools(q);
    }

    @GetMapping("/chat/cheap")
    public String cheapAgent(@RequestParam String q) {
        return chatService.chatCheap(q);
    }

    @GetMapping("/chat/cheapTool")
    public String cheapTool(@RequestParam String q) {
        return chatService.chatCheapWithTools(q);
    }

    @GetMapping("/chat/local")
    public String localAgent(@RequestParam String q) {
        return chatService.chatLocal(q);
    }

    @GetMapping("/chat/localTool")
    public String localTool(@RequestParam String q) {
        return chatService.chatLocalWithTools(q);
    }


    /**
     * 流式对话（SSE）
     * 访问: http://localhost:8080/chat/stream?q=写一首诗
     * 注意: curl 用 -N 才能看到流式效果
     */
    @GetMapping(value = "/chat/deepseek/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatDeepStream(@RequestParam("q") String question) {
        return chatService.deepseekChatStream(question);
    }



    /**
     * 流式对话（SSE）
     * 访问: http://localhost:8080/chat/stream?q=写一首诗
     * 注意: curl 用 -N 才能看到流式效果
     */
    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestParam("q") String question) {
        return chatService.chatStream(question);
    }

    /**
     * 专家模式（带 System Prompt）
     * 访问: http://localhost:8080/chat/expert?q=MySQL还是PostgreSQL
     */
    @GetMapping("/chat/expert")
    public String expert(@RequestParam("q") String question) {
        return chatService.chatAsExpert(question);
    }

    /**
     * 行业客服（Prompt 模板 + 变量）
     * 访问: http://localhost:8080/chat/industry?industry=电子产品&q=保修期多久
     */
    @GetMapping("/chat/industry")
    public String industry(
            @RequestParam("industry") String industry,
            @RequestParam("q") String question) {
        return chatService.industryCustomerService(industry, question);
    }

    /**
     * 结构化输出 - 菜谱生成
     * 访问: POST http://localhost:8080/chat/recipe?dish=番茄炒蛋
     */
    @PostMapping("/chat/recipe")
    public Recipe recipe(@RequestParam("dish") String dish) {
        return chatService.generateRecipe(dish);
    }
}
