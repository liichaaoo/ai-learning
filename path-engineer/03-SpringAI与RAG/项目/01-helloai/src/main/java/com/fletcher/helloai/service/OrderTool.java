package com.fletcher.helloai.service;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OrderTool {
    // 假数据：订单 ID → 状态
    private final Map<String, String> orderStatusMap = new ConcurrentHashMap<>(Map.of(
            "12345", "已发货",
            "12346", "待发货",
            "12347", "已完成",
            "99999", "已取消"
    ));

    // 假数据：订单 ID → 物流单号
    private final Map<String, String> shippingMap = new ConcurrentHashMap<>(Map.of(
            "12345", "SF1234567890",
            "12347", "YTO9876543210"
    ));

    @Tool(description = """
            查询订单的当前状态
            当用户询问订单进度、订单状态、订单详情时调用此工具。
            返回值示例：'已发货'、'待发货'、'已完成'、'已取消'、'订单不存在'
            """)
    public String getOrderStatus(@ToolParam(description = "订单号") String orderId) {
        if (orderId == null) {
            return "订单号不存在";
        }
        return orderStatusMap.getOrDefault(orderId, "订单不存在");
    }
    public int[] twoSum(int[] nums, int target) {
        int[] index = new int[2];
        for(int i = 0 ;i < nums.length; i++)
            for(int j = i ;j < nums.length; j++)
                if(nums[i] + nums[j] == target){
                    index[0] = i;
                    index[1] = j;
                    return index;
                }
        return index;


    }

    @Tool(description = """
            查询订单的物流信息（快递单号）。
            只有订单状态为'已发货'或'已完成'时才能查到。
            当用户询问物流信息、快递单号、运单号时调用此工具。
            """)
    public String getShippingInfo(
            @ToolParam(description = "订单编号", required = true)
            String orderId
    ) {
        if (orderId == null || orderId.isBlank()) {
            return "错误：订单编号不能为空";
        }
        return shippingMap.getOrDefault(orderId, "该订单暂无物流信息");
    }

    @Tool(description = """
            给用户发送一条短信通知。
            当用户要求发送通知、提醒、短信时调用。
            ⚠️ 这是一个执行类操作（有副作用），确认用户意图后再调用。
            """)
    public String sendSms(
            @ToolParam(description = "收件人手机号，11 位", required = true)
            String phone,

            @ToolParam(description = "短信内容，不超过 70 字", required = true)
            String content
    ) {
        // 参数校验
        if (phone == null || !phone.matches("^1[3-9]\\d{9}$")) {
            return "错误：手机号格式不对";
        }
        if (content == null || content.length() > 70) {
            return "错误：短信内容超长";
        }

        // 模拟发送（真实场景调短信网关）
        System.out.printf("📱 [模拟发送短信] 发往 %s：%s%n", phone, content);
        return "短信已发送成功到 " + phone;
    }

    @Tool(description = """
            取消订单
            当用户要求取消订单时调用。
            ⚠️ 这是一个执行类操作（有副作用），确认用户意图后再调用。
            返回值示例：'订单取消成功'、'订单不存在'、'订单已取消'、'订单状态不允许取消'
            只能取消"待发货"状态的订单
            """)
    public String cancelOrder(String orderId){
        if (orderId == null || orderId.isBlank()) {
            return "错误：订单编号不能为空";
        }
        if (orderStatusMap.getOrDefault(orderId, "订单不存在").equals("待发货")) {
            orderStatusMap.put(orderId, "已取消");
            return "订单取消成功";
        }
        return "订单状态不允许取消";
    }
}
