"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/utils/PR_util.py
Description: 
"""
import httpx
from loguru import logger
def get_existing_ai_comment_id(
    repo_full_name: str, pr_number: int, headers: dict, COMMENT_MARKER: str
) -> int | None:
    """检查是否存在 AI 评论，若存在返回 comment_id，否则返回 None"""
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    try:
        resp = httpx.get(url, headers=headers,timeout=10)
        if resp.status_code != 200:
            logger.error("⚠️ 获取已有评论失败，跳过去重检查")
            return None

        comments = resp.json()
        for comment in comments:
            if COMMENT_MARKER in comment.get("body", ""):
                return comment["id"]  # 返回 comment_id
        return None
    except Exception as e:
        logger.error(f"⚠️ 获取已有评论失败，跳过去重检查: {e}")
        return None
