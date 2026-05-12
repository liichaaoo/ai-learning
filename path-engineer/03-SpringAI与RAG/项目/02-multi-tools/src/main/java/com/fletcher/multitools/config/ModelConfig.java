package com.fletcher.multitools.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 多模型配置
 *
 * 同时配置了通义千问（via OpenAI starter）+ Ollama（本地）
 * 通过 Bean name 区分，注入时用 @Qualifier("xxxClient")
 */
@Configuration
public class ModelConfig {

    @Bean("qwenClient")
    public ChatClient qwenClient(OpenAiChatModel openAiChatModel) {
        return ChatClient.builder(openAiChatModel).build();
    }

    @Bean("ollamaClient")
    public ChatClient ollamaClient(OllamaChatModel ollamaChatModel) {
        return ChatClient.builder(ollamaChatModel).build();
    }
}
