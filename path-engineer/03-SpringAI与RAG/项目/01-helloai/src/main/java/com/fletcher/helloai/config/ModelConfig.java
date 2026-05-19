package com.fletcher.helloai.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ModelConfig {

    /**
     * 通义千问 ChatClient（走 OpenAI 兼容协议）
     * 使用 name="qwenClient" 以便注入时区分
     */
    @Bean("qwenClient")
    public ChatClient qwenClient(OpenAiChatModel openAiChatModel) {
        return ChatClient.builder(openAiChatModel).build();
    }

    /**
     * Ollama 本地模型 ChatClient
     */
    @Bean("ollamaClient")
    public ChatClient ollamaClient(OllamaChatModel ollamaChatModel) {
        return ChatClient.builder(ollamaChatModel).build();
    }

    @Bean("deepseekClient")
    public ChatClient deepseekClient(@Qualifier("deepseekChatModel") OpenAiChatModel model) {
        return ChatClient.builder(model).build();
    }

    @Bean("deepseekChatModel")
    public OpenAiChatModel deepseekChatModel() {
        OpenAiApi api = OpenAiApi.builder()
            .baseUrl("https://api.deepseek.com")
            .apiKey(System.getenv("DEEPSEEK_API_KEY"))
            .build();

        OpenAiChatOptions options = OpenAiChatOptions.builder()
                .model("deepseek-chat")     // 或 "deepseek-reasoner"
                .temperature(0.7)
                .build();

        return OpenAiChatModel.builder()
                .openAiApi(api)
                .defaultOptions(options)
                .build();
    }
}
