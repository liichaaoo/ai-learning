package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OrderTool {

    private final Map<String, String> orderStatusMap = new ConcurrentHashMap<>(Map.of(
            "12345", "已发货",
            "12346", "待发货",
            "12347", "已完成",
            "99999", "已取消"
    ));

    private final Map<String, String> shippingMap = new ConcurrentHashMap<>(Map.of(
            "12345", "SF1234567890",
            "12347", "YTO9876543210"
    ));

    @Tool(description = """
            查询订单的当前状态。
            用户询问订单进度、订单状态时调用。
            返回示例：'已发货'、'待发货'、'已完成'、'已取消'、'订单不存在'
            """)
    public String getOrderStatus(
            @ToolParam(description = "订单编号，数字字符串，例如 12345", required = true) String orderId) {
        if (orderId == null || orderId.isBlank()) return "错误：订单编号不能为空";
        return orderStatusMap.getOrDefault(orderId, "订单不存在");
    }

    @Tool(description = """
            查询订单的物流单号（运单号）。
            仅'已发货'或'已完成'的订单有物流信息。
            """)
    public String getShippingInfo(
            @ToolParam(description = "订单编号", required = true) String orderId) {
        if (orderId == null || orderId.isBlank()) return "错误：订单编号不能为空";
        return shippingMap.getOrDefault(orderId, "该订单暂无物流信息");
    }

    @Tool(description = """
            给指定手机号发送短信通知。
            ⚠️ 这是执行类操作，确认用户意图后再调用。
            """)
    public String sendSms(
            @ToolParam(description = "收件人手机号，11 位", required = true) String phone,
            @ToolParam(description = "短信内容，不超过 70 字", required = true) String content) {
        if (phone == null || !phone.matches("^1[3-9]\\d{9}$")) return "错误：手机号格式不对";
        if (content == null || content.length() > 70) return "错误：短信内容超长";
        System.out.printf("📱 [模拟发送] → %s: %s%n", phone, content);
        return "短信已发送到 " + phone;
    }
}
