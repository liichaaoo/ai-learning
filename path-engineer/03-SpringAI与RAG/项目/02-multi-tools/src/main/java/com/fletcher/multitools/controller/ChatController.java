package com.fletcher.multitools.controller;

import com.fletcher.multitools.service.ChatService;
import com.fletcher.multitools.service.ModelRouterService;
import com.fletcher.multitools.service.OpsAgentService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

/**
 * 所有接口集中在这里，按 Day 分组便于学习对照
 */
@RestController
public class ChatController {

    private final ChatService chatService;
    private final ModelRouterService routerService;
    private final OpsAgentService opsAgentService;

    public ChatController(ChatService chatService,
                          ModelRouterService routerService,
                          OpsAgentService opsAgentService) {
        this.chatService = chatService;
        this.routerService = routerService;
        this.opsAgentService = opsAgentService;
    }

    // ==================== Day 1-2: Function Calling ====================

    @GetMapping("/chat/agent")
    public String agent(@RequestParam String q) {
        return chatService.chatCheapWithTools(q);
    }

    // ==================== Day 3: 多模型 ====================

    @GetMapping("/chat/cheap")
    public String cheap(@RequestParam String q) {
        return chatService.chatCheap(q);
    }

    @GetMapping("/chat/local")
    public String local(@RequestParam String q) {
        return chatService.chatLocal(q);
    }

    @GetMapping("/chat/agent-local")
    public String agentLocal(@RequestParam String q) {
        return chatService.chatLocalWithTools(q);
    }

    // ==================== Day 4: 路由 & 降级 ====================

    @GetMapping("/chat/auto")
    public String auto(@RequestParam String q) {
        return routerService.routeByComplexity(q);
    }

    @GetMapping("/chat/privacy")
    public String privacy(@RequestParam String q) {
        return routerService.routeByPrivacy(q);
    }

    @GetMapping("/chat/safe")
    public String safe(@RequestParam String q) {
        return routerService.callWithFallback(q);
    }

    @GetMapping("/chat/smart")
    public String smart(@RequestParam String q) {
        return routerService.smartRoute(q);
    }

    // ==================== Day 5: 运维助手（毕业项目）====================

    @GetMapping("/ops")
    public String ops(@RequestParam String q) {
        return opsAgentService.askSync(q);
    }

    @GetMapping(value = "/ops/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> opsStream(@RequestParam String q) {
        return opsAgentService.ask(q);
    }
}
