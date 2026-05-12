package com.fletcher.helloai.dto;

import java.util.List;

/**
 * 结构化输出示例 - 菜谱
 *
 * Spring AI 的 .entity(Recipe.class) 会：
 *   1. 自动根据字段生成 JSON Schema 塞进 Prompt
 *   2. 让 LLM 返回符合 Schema 的 JSON
 *   3. Jackson 自动反序列化成这个 record
 */
public record Recipe(
        String name,                // 菜名
        int difficulty,             // 难度 1-5
        int cookTime,               // 预估耗时（分钟）
        List<String> ingredients,   // 食材列表
        List<String> steps          // 步骤
) {
}
