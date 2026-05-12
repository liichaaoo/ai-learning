package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 运维监控工具（Day 5 毕业项目核心）
 * 真实场景会对接 Prometheus / K8s / 告警系统，这里用假数据演示。
 */
@Service
public class SystemMonitorTool {

    private static final List<String> ALLOWED_SERVICES = List.of(
            "prod-api-01", "prod-api-02", "prod-api-03",
            "staging-api-01", "dev-api-01"
    );

    @Tool(description = """
            获取指定服务的 CPU 使用率（百分比字符串，如 "45%"）。
            用户询问服务性能、CPU、卡顿、慢时调用。
            """)
    public String getCpuUsage(@ToolParam(description = "服务名，如 prod-api-01") String serviceName) {
        if (!ALLOWED_SERVICES.contains(serviceName)) return "错误：服务不在监控列表";
        return ThreadLocalRandom.current().nextInt(20, 95) + "%";
    }

    @Tool(description = """
            获取指定服务的内存使用率（百分比字符串）。
            用户询问内存、OOM、吃内存时调用。
            """)
    public String getMemoryUsage(@ToolParam(description = "服务名") String serviceName) {
        if (!ALLOWED_SERVICES.contains(serviceName)) return "错误：服务不在监控列表";
        return ThreadLocalRandom.current().nextInt(30, 95) + "%";
    }

    @Tool(description = "获取指定服务最近的错误日志列表。用户问'报错'、'错误'、'异常'时调用。")
    public List<String> getRecentErrors(
            @ToolParam(description = "服务名") String serviceName,
            @ToolParam(description = "返回最近几条，建议 10") int count) {
        if (!ALLOWED_SERVICES.contains(serviceName)) return List.of("错误：服务不在监控列表");
        if (count < 1 || count > 50) count = 10;
        List<String> logs = List.of(
                "2026-05-12 22:31:05 ERROR OutOfMemoryError: Java heap space",
                "2026-05-12 22:31:08 ERROR Connection refused to db-master:3306",
                "2026-05-12 22:31:10 ERROR TimeoutException on GET /api/orders/12345"
        );
        return logs.subList(0, Math.min(count, logs.size()));
    }

    @Tool(description = """
            重启指定服务。⚠️ 危险操作。
            只有用户明确同意（说"重启"、"执行"、"确认"）后才调用。
            只是询问状态或请求建议时不要调用。
            """)
    public String restartService(@ToolParam(description = "服务名") String serviceName) {
        if (!ALLOWED_SERVICES.contains(serviceName))
            return "错误：服务 " + serviceName + " 不在白名单";
        System.out.printf("⚠️ [模拟重启] %s 成功%n", serviceName);
        return "服务 " + serviceName + " 已重启";
    }

    @Tool(description = "发送告警通知。发现严重问题或执行重要操作后调用。")
    public String sendAlert(
            @ToolParam(description = "告警级别：INFO / WARN / CRITICAL") String level,
            @ToolParam(description = "告警内容，≤ 200 字") String message) {
        if (message == null || message.length() > 200) return "错误：内容超长或为空";
        if (!List.of("INFO", "WARN", "CRITICAL").contains(level)) return "错误：级别不合法";
        System.out.printf("🔔 [%s] %s%n", level, message);
        return "告警已发送（" + level + "）";
    }
}
