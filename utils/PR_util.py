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
import httpx
from typing import Dict, Optional
from loguru import logger

def get_existing_ai_comment_id(
    repo_full_name: str, pr_number: int, headers: Dict[str, str], COMMENT_MARKER: str
) -> Optional[int]:
    """
    检查 PR 中是否存在 AI 评论，若存在返回 comment_id，否则返回 None
    
    Args:
        repo_full_name: 仓库全名 (如 "owner/repo")
        pr_number: PR 编号
        headers: API 请求头，包含认证信息
        COMMENT_MARKER: 用于识别 AI 评论的标记文本
        
    Returns:
        int | None: 找到的评论 ID，未找到则返回 None
    """
    # 输入验证
    if not repo_full_name or pr_number <= 0 or not COMMENT_MARKER:
        logger.warning("⚠️ 输入参数无效，跳过去重检查")
        return None
        
    # URL 安全构造
    try:
        import urllib.parse
        encoded_repo = urllib.parse.quote(repo_full_name, safe='/')
        url = f"https://api.github.com/repos/{encoded_repo}/issues/{pr_number}/comments"
    except Exception:
        logger.error("⚠️ 构造 URL 失败，仓库名或 PR 号格式错误")
        return None
    
    try:
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.error(f"⚠️ 获取已有评论失败，状态码: {resp.status_code}，跳过去重检查")
            return None

        comments = resp.json()
        if not isinstance(comments, list):
            logger.error("⚠️ API 响应格式异常，跳过去重检查")
            return None
            
        for comment in comments:
            if isinstance(comment, dict) and COMMENT_MARKER in comment.get("body", ""):
                return comment["id"]
        return None
    except httpx.RequestError as e:
        logger.error(f"⚠️ HTTP 请求失败，跳过去重检查: {e}")
        return None
    except KeyError as e:
        logger.error(f"⚠️ 解析响应数据失败，跳过去重检查: {e}")
        return None
    except Exception as e:
        logger.error(f"⚠️ 获取已有评论失败，跳过去重检查: {e}")
        return None