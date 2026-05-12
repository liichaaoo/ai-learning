package com.fletcher.multitools;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Week 2 毕业项目 - 多工具 + 多模型 AI 助手
 * 启动后访问：
 *   http://localhost:8080          → 演示页
 *   http://localhost:8080/ops?q=   → 智能运维助手
 */
@SpringBootApplication
public class MultiToolsApplication {
    public static void main(String[] args) {
        SpringApplication.run(MultiToolsApplication.class, args);
    }
}
