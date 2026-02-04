"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-07
FilePath: /test/utils/qwen.py
Description: 
"""
import httpx
import logging

logger = logging.getLogger(__name__)

def get_diff(single_file_diff: str, DASHSCOPE_API_KEY: str) -> str:
    COMMENT_MARKER = "🤖 **AI Code Review"  # 用于识别是否已有 AI 评论
    prompt = f"""
        你是一位资深软件工程师，请对以下代码变更进行审查。关注：
        - 潜在 bug（空指针、越界、资源泄漏等）
        - 安全风险（硬编码密钥、SQL 注入等）
        - 代码风格、可读性、可维护性
        - 性能问题
        - 是否符合最佳实践

        请用中文回答，每条意见以"\\n- [类型] 描述"格式列出。若无问题，回复"✅ 未发现明显问题"。

        以下是变更的代码文件：

        {single_file_diff}
    """
    
    try:
        qwen_resp = httpx.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen-max",
                "input": {"messages": [{"role": "user", "content": prompt}]},
                "parameters": {"result_format": "message"}
            },
            timeout=60.0
        )
    except httpx.RequestError as e:
        logger.error(f"❌ 调用 Qwen API 失败: {e}")
        return ""

    if qwen_resp.status_code != 200:
        logger.error("❌ Qwen 调用失败:", qwen_resp.text)
        return ""
    else:
        try:
            review_text = qwen_resp.json()["output"]["choices"][0]["message"]["content"]
            # 这里不再添加评论标记，因为汇总函数会处理
            return review_text
        except (KeyError, IndexError) as e:
            logger.error(f"解析 Qwen 响应失败: {e}")
            return ""