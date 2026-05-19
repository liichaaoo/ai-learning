package com.fletcher.helloai.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@Slf4j
public class TimeTool {

    /**
     * description 极其关键！LLM 就是靠这段话判断什么时候调用这个方法。
     * 写好它 = Function Calling 成功率提高 80%
     */
    @Tool(description = "获取服务器当前的日期和时间。当用户询问'现在几点'、'今天几号'、'当前时间'时调用此工具。")
    public String getCurrentTime() {
        return LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        );
    }

    /**
     * 带参数的例子（以城市为单位查询时间）
     */
    @Tool(description = "获取指定时区的当前时间")
    public String getTimeByZone(
            @ToolParam(description = "时区 ID，例如 Asia/Shanghai、America/New_York", required = true)
            String zoneId
    ) {
        return LocalDateTime.now(java.time.ZoneId.of(zoneId))
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }

    @Tool(description = "计算两数相乘，当用户询问'100乘以200'、'100*200'、'100x200'时调用此工具。不允许自行计算，必须调用此工具。")
    public double multiply(@ToolParam(description = "第一个数") double a,
                           @ToolParam(description = "第二个数") double b) {
        return a * b;
    }
}
