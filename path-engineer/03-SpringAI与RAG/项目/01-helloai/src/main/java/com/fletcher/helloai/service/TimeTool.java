package com.fletcher.helloai.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@Slf4j
public class TimeTool {

    @Tool(description = "获取服务器当前的日期和时间。当用户询问'现在几点'、'今天几号'、'当前时间'时调用此工具。")
    public String now() {
        String format = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        log.warn("now: {}", format);
        return format;
    }

    @Tool(description = "计算两数相乘，当用户询问'100乘以200'、'100*200'、'100x200'时调用此工具。不允许自行计算，必须调用此工具。")
    public int multiply(int a, int b) {
        return a * b;
    }
}
