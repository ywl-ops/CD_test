"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/utils/PR_util.py
Description: 
"""
# 文件开头只需要一次
import httpx
import urllib.parse
from typing import Dict, Optional
from loguru import logger


def get_existing_ai_comment_id(
    repo_full_name: str,
    pr_number: int,
    headers: Dict[str, str],
    comment_marker: str,
    timeout: float = 10.0,
) -> Optional[int]:
    """
    检查 PR 中是否存在 AI 评论，若存在返回 comment_id，否则返回 None
    
    Args:
        repo_full_name: 仓库全名 (如 "owner/repo")
        pr_number: PR 编号
        headers: API 请求头，包含认证信息
        comment_marker: 用于识别 AI 评论的标记文本
        timeout: 请求超时时间（秒），默认10.0

    Returns:
        int | None: 找到的评论 ID，未找到则返回 None
    """
    if not repo_full_name or pr_number <= 0 or not comment_marker:
        logger.warning("⚠️ Invalid input parameters, skipping deduplication check")
        return None

    # URL construction with proper encoding
    try:
        encoded_repo = urllib.parse.quote(repo_full_name, safe='/')
        url = f"https://api.github.com/repos/{encoded_repo}/issues/{pr_number}/comments"
    except Exception as e:
        logger.error(f"⚠️ Failed to construct URL: {str(e)}")
        return None

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)

        # Handle HTTP errors
        response.raise_for_status()  # This will raise HTTPStatusError for 4xx/5xx responses

        comments = response.json()
        if not isinstance(comments, list):
            logger.error("⚠️ API response format error, skipping deduplication check")
            return None

        for comment in comments:
            if isinstance(comment, dict) and comment_marker in comment.get("body", ""):
                return comment.get("id")
        return None

    except httpx.TimeoutException:
        logger.error("⚠️ Request timeout")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"⚠️ GitHub API returned error status: {e.response.status_code}")
        return None
    except ValueError as e:  # JSON parsing error
        logger.error(f"⚠️ Response format error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"⚠️ Unexpected error occurred: {str(e)}")
        return None
