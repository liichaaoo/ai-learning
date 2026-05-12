package com.fletcher.multitools.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

/**
 * 多模型路由器 - Day 4 核心
 */
@Service
public class ModelRouterService {

    private final ChatClient qwenClient;
    private final ChatClient ollamaClient;

    public ModelRouterService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            @Qualifier("ollamaClient") ChatClient ollamaClient) {
        this.qwenClient = qwenClient;
        this.ollamaClient = ollamaClient;
    }

    /** 按复杂度路由 */
    public String routeByComplexity(String q) {
        Complexity c = judgeComplexity(q);
        return switch (c) {
            case SIMPLE -> {
                log("SIMPLE → qwen-turbo");
                yield qwenClient.prompt().user(q).call().content();
            }
            case COMPLEX -> {
                log("COMPLEX → qwen (理想情况下换 qwen-max/gpt-4o)");
                yield qwenClient.prompt().user(q).call().content();
            }
            case SENSITIVE -> {
                log("SENSITIVE → ollama (本地)");
                yield ollamaClient.prompt().user(q).call().content();
            }
        };
    }

    /** 按隐私路由 */
    public String routeByPrivacy(String q) {
        if (containsSensitiveKeyword(q)) {
            log("PRIVACY → ollama");
            return ollamaClient.prompt().user(q).call().content();
        }
        log("PUBLIC → qwen");
        return qwenClient.prompt().user(q).call().content();
    }

    /** 带降级 */
    public String callWithFallback(String q) {
        try {
            return qwenClient.prompt().user(q).call().content();
        } catch (Exception e) {
            log("FALLBACK → ollama, reason: " + e.getMessage());
            return ollamaClient.prompt().user(q).call().content();
        }
    }

    /** 用小模型做分类路由（进阶） */
    public String smartRoute(String q) {
        String category = qwenClient
                .prompt()
                .system("""
                        你是任务分类器。下面的用户问题属于哪一类？
                        只返回分类 ID，不要多说。
                        - simple: 闲聊、问候、事实
                        - code: 代码相关
                        - reasoning: 数学推理
                        - sensitive: 合同、密码、薪资等敏感
                        """)
                .user(q).call().content().trim().toLowerCase();

        log("smartRoute classified as: " + category);
        if (category.contains("sensitive")) {
            return ollamaClient.prompt().user(q).call().content();
        }
        return qwenClient.prompt().user(q).call().content();
    }

    private enum Complexity { SIMPLE, COMPLEX, SENSITIVE }

    private Complexity judgeComplexity(String q) {
        if (containsSensitiveKeyword(q)) return Complexity.SENSITIVE;
        boolean hasCode = q.contains("代码") || q.contains("算法") || q.contains("实现");
        if (q.length() > 100 || hasCode) return Complexity.COMPLEX;
        return Complexity.SIMPLE;
    }

    private boolean containsSensitiveKeyword(String q) {
        if (q == null) return false;
        return q.contains("合同") || q.contains("内部") || q.contains("密码")
                || q.contains("身份证") || q.contains("薪资");
    }

    private void log(String msg) {
        System.out.println("[ROUTER] " + msg);
    }
}
