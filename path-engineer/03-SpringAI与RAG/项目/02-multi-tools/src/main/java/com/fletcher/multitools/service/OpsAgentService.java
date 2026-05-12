package com.fletcher.multitools.service;

import com.fletcher.multitools.tools.SystemMonitorTool;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

/**
 * Week 2 毕业项目：AI 智能运维助手
 */
@Service
public class OpsAgentService {

    private static final String SYSTEM_PROMPT = """
            你是一位资深运维工程师 AI 助手，名叫 OpsAgent。

            工作原则：
            1. 用户问服务状态时，主动调用监控工具查询真实数据，不要编造
            2. 发现严重问题（CPU > 80%、内存 > 85%、大量错误）时主动提示风险
            3. 执行危险操作（重启、发告警）前确认用户意图，不要擅自操作
            4. 所有数据查询完后，给出简洁的分析结论和行动建议
            5. 回答用 markdown 列表格式，方便快速扫读

            可用工具：
            - 查询 CPU / 内存 / 错误日志
            - 重启服务（需用户确认）
            - 发送告警（INFO/WARN/CRITICAL）
            """;

    private final ChatClient qwenClient;
    private final SystemMonitorTool monitorTool;

    public OpsAgentService(
            @Qualifier("qwenClient") ChatClient qwenClient,
            SystemMonitorTool monitorTool) {
        this.qwenClient = qwenClient;
        this.monitorTool = monitorTool;
    }

    public String askSync(String question) {
        return qwenClient.prompt()
                .system(SYSTEM_PROMPT)
                .user(question)
                .tools(monitorTool)
                .call()
                .content();
    }

    public Flux<String> ask(String question) {
        return qwenClient.prompt()
                .system(SYSTEM_PROMPT)
                .user(question)
                .tools(monitorTool)
                .stream()
                .content();
    }
}
