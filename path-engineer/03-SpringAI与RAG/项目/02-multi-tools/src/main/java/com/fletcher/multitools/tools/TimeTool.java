package com.fletcher.multitools.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

@Service
public class TimeTool {

    @Tool(description = """
            获取服务器当前的日期和时间。
            当用户询问'现在几点'、'今天几号'、'当前时间'时调用此工具。
            返回格式：yyyy-MM-dd HH:mm:ss
            """)
    public String getCurrentTime() {
        return LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        );
    }

    @Tool(description = "获取指定时区的当前时间，例如查询纽约、东京等海外城市时间")
    public String getTimeByZone(
            @ToolParam(description = "时区 ID，例如 Asia/Shanghai、America/New_York、Europe/London", required = true)
            String zoneId
    ) {
        try {
            return LocalDateTime.now(ZoneId.of(zoneId))
                    .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        } catch (Exception e) {
            return "错误：无效的时区 " + zoneId;
        }
    }
}
