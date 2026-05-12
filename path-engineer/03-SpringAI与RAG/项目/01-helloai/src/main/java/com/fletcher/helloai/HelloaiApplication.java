package com.fletcher.helloai;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Hello Spring AI - Week 1 毕业项目
 *
 * 启动后访问：
 *   http://localhost:8080            → 演示页面
 *   http://localhost:8080/chat?q=你好  → 同步对话
 */
@SpringBootApplication
public class HelloaiApplication {

    public static void main(String[] args) {
        SpringApplication.run(HelloaiApplication.class, args);
    }

}
