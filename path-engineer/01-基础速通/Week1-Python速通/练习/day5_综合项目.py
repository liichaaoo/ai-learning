"""
Day 5 · 综合项目：批量调用 LLM API
================================

把 Week 1 学的所有招式攒一起，做一个真正能跑的小工具。
这是阶段 3 (Spring AI) 的预热，今天就让你"亲手碰"大模型。

运行前准备：
  1. pip install openai pandas tqdm
  2. 申请通义千问 API Key（或 OpenAI）
     通义千问：https://dashscope.aliyun.com/
  3. 设置环境变量：
     export DASHSCOPE_API_KEY="sk-xxx"
  4. 运行：python3 day5_综合项目.py

如果跑不通，去 Day5-综合演练.md 看详细步骤。
"""

import os
import time
import json
from functools import wraps
from typing import Optional, List, Dict
from contextlib import contextmanager


# ----------------------------------------------------------------------
# 步骤 0：配置区（可改）
# ----------------------------------------------------------------------

API_KEY = os.environ.get("DASHSCOPE_API_KEY")  # 不要硬编码 API Key！
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-turbo"
SYSTEM_PROMPT = "你是一个专业、简洁的 AI 助手。回答控制在 100 字以内。"

# 你想问的问题列表（自由修改）
QUESTIONS = [
    "用一句话解释什么是大语言模型（LLM）",
    "Spring AI 是什么？",
    "RAG 是什么？解决什么问题？",
    "向量数据库有哪些主流选择？",
    "什么是 Function Calling？",
]


# ----------------------------------------------------------------------
# 步骤 1：装饰器（用 Day 3 学的）
# ----------------------------------------------------------------------

def timing(func):
    """测量函数耗时的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  ⏱  {func.__name__} 耗时 {elapsed:.2f}s")
        return result
    return wrapper


def retry(max_times: int = 3, delay: float = 1.0):
    """异常时自动重试装饰器（Day 3 题 3.2 的强化版）"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"  ⚠  第 {attempt}/{max_times} 次失败: {e}")
                    if attempt < max_times:
                        time.sleep(delay * attempt)
            raise last_error
        return wrapper
    return decorator


# ----------------------------------------------------------------------
# 步骤 2：上下文管理器（用 Day 3 学的）
# ----------------------------------------------------------------------

@contextmanager
def progress_block(name: str):
    """显示一段处理的开始和结束"""
    print(f"\n[ {name} ] 开始")
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"[ {name} ] 完成，总耗时 {elapsed:.2f}s\n")


# ----------------------------------------------------------------------
# 步骤 3：核心调用函数
# ----------------------------------------------------------------------

@retry(max_times=3, delay=1.0)
def ask_llm(question: str, system_prompt: str = SYSTEM_PROMPT) -> str:
    """
    调用 LLM API，返回回答。

    :param question: 用户问题
    :param system_prompt: 系统提示词
    :return: LLM 的回答内容
    :raises: 网络错误、API 错误等（已被 retry 捕获）
    """
    # 延迟导入，方便没装包时只跑前面部分
    from openai import OpenAI

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content


# ----------------------------------------------------------------------
# 步骤 4：批量处理（用 Day 2 的推导式 + Day 3 的异常处理）
# ----------------------------------------------------------------------

def batch_ask(questions: List[str]) -> List[Dict[str, str]]:
    """批量调用 LLM，返回结果列表"""
    results = []
    total = len(questions)

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{total}] 问题: {q}")
        try:
            answer = ask_llm(q)
            print(f"  ✅ 回答: {answer[:80]}...")
            results.append({
                "index": i,
                "question": q,
                "answer": answer,
                "status": "ok",
            })
        except Exception as e:
            print(f"  ❌ 最终失败: {e}")
            results.append({
                "index": i,
                "question": q,
                "answer": "",
                "status": f"error: {e}",
            })

    return results


# ----------------------------------------------------------------------
# 步骤 5：保存结果（用 Day 3 的 with）
# ----------------------------------------------------------------------

def save_to_json(results: List[Dict], filename: str = "llm_answers.json"):
    """保存为 JSON 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存到 {filename}")


def save_to_markdown(results: List[Dict], filename: str = "llm_answers.md"):
    """保存为 Markdown 文件（更易读）"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# LLM 批量问答结果\n\n")
        f.write(f"模型: {MODEL}\n\n")
        f.write(f"问题数: {len(results)}\n\n")
        f.write("---\n\n")

        for r in results:
            f.write(f"## {r['index']}. {r['question']}\n\n")
            if r["status"] == "ok":
                f.write(f"{r['answer']}\n\n")
            else:
                f.write(f"❌ {r['status']}\n\n")
            f.write("---\n\n")
    print(f"✅ 已保存到 {filename}")


# ----------------------------------------------------------------------
# 步骤 6：统计（用 Day 4 的 NumPy / Day 2 的字典推导式）
# ----------------------------------------------------------------------

def print_stats(results: List[Dict]):
    """打印统计信息"""
    total = len(results)
    success = sum(1 for r in results if r["status"] == "ok")
    failed = total - success

    print("\n" + "=" * 50)
    print("📊 统计")
    print("=" * 50)
    print(f"总问题数: {total}")
    print(f"成功:    {success}")
    print(f"失败:    {failed}")
    print(f"成功率:  {success / total * 100:.1f}%")

    # 用字典推导式统计每个回答的字数（Day 2 招式）
    if success > 0:
        word_counts = {
            r["index"]: len(r["answer"])
            for r in results
            if r["status"] == "ok"
        }
        avg = sum(word_counts.values()) / len(word_counts)
        print(f"平均回答长度: {avg:.0f} 字")


# ----------------------------------------------------------------------
# 主程序入口
# ----------------------------------------------------------------------

def main():
    # 检查 API Key
    if not API_KEY:
        print("❌ 没有设置 DASHSCOPE_API_KEY 环境变量")
        print("请先 export DASHSCOPE_API_KEY='你的 key'")
        print("\n申请地址：https://dashscope.aliyun.com/")
        return

    print("=" * 50)
    print("🚀 LLM 批量问答工具")
    print("=" * 50)
    print(f"模型: {MODEL}")
    print(f"问题数: {len(QUESTIONS)}")
    print()

    # 用上下文管理器包一层
    with progress_block("批量调用 LLM"):
        results = batch_ask(QUESTIONS)

    # 保存结果
    with progress_block("保存结果"):
        save_to_json(results)
        save_to_markdown(results)

    # 打印统计
    print_stats(results)

    print("\n🎉 完成！打开 llm_answers.md 看结果")


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------
# 📝 你的任务（按顺序做）
# ----------------------------------------------------------------------
"""
任务清单：

[ ] 1. 申请通义千问 API Key 并设置环境变量
       export DASHSCOPE_API_KEY="sk-xxx"

[ ] 2. 安装依赖
       pip install openai

[ ] 3. 直接运行本文件，看能不能跑通
       python3 day5_综合项目.py

[ ] 4. 修改 QUESTIONS 列表为你真正想问的问题
       比如学习中遇到的问题

[ ] 5. 修改 SYSTEM_PROMPT，让 AI 用不同风格回答
       比如：'你是一个 Java 资深工程师，从工程角度回答'

[ ] 6. 故意让一次调用失败（比如把 API Key 改错），
       看 retry 装饰器能不能重试 3 次

[ ] 7. （选做）改成读 CSV 而不是写在代码里
       - 用 pandas 读 CSV
       - 列名 'question' 作为问题
       - 把答案写回新列 'answer'

[ ] 8. （选做）加 tqdm 进度条
       pip install tqdm
       from tqdm import tqdm
       for q in tqdm(QUESTIONS): ...

[ ] 9. （选做）把代码 push 到自己的 GitHub
       这就是你的第一个 AI 应用 demo
"""
