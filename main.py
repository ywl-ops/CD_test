"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/main.py
Description: AI驱动的PR代码审查工具
"""

# 标准库导入
import os

# 第三方库导入
from loguru import logger
import httpx

# 本地应用/库导入
from read_toml import read_toml
from utils.PR_util import get_existing_ai_comment_id
from utils.agno_agent import Model

# 在文件顶部定义常量
MAX_PATCH_LENGTH = 40000  # 最大补丁长度
HTTP_TIMEOUT = 30.0       # HTTP请求超时时间
def get_pr_files(repo_full_name, pr_number, headers):
    """获取PR的所有变更文件"""
    files_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    
    try:
        resp = httpx.get(files_url, headers=headers, timeout=HTTP_TIMEOUT)
        if resp.status_code != 200:
            logger.error(f"❌ 获取文件列表失败: {resp.text}")
            return None
        
        return resp.json()
    except httpx.RequestError as e:
        logger.error(f"请求PR文件时发生错误: {e}")
        return None

def filter_code_patches(files,CODE_EXTENSIONS):
    """过滤出需要审查的代码补丁"""
    filtered_patches = []
    
    for f in files:
        filename = f["filename"]
        status = f.get("status", "")
        patch = f.get("patch", "")

        # 跳过删除的文件
        if status == "removed":
            logger.info(f"🗑️ 跳过已删除文件: {filename}")
            continue

        # 判断是否为代码文件
        _, ext = os.path.splitext(filename.lower())
        if ext not in CODE_EXTENSIONS:
            logger.info(f"📄 跳过非代码文件: {filename}")
            continue

        if not patch.strip():
            logger.info(f"📄 跳过空变更文件: {filename}")
            continue

        filtered_patches.append({
            "filename": filename,
            "patch": f"--- {filename} ---\n{patch}"
        })
    
    return filtered_patches

def truncate_patch(patch, max_length=MAX_PATCH_LENGTH):
    """截断单个文件补丁内容，避免超出API限制"""
    if len(patch) <= max_length:
        return patch
    return patch[:max_length] + "\n...（内容过长，已截断）"

def process_single_file(filename, patch,PR_NUMBER,agent):
    """处理单个文件的代码审查"""
    logger.info(f"🧠 正在审查文件: {filename}")
    truncated_patch = truncate_patch(patch)
    review_result = agent.generate_code_review(truncated_patch,PR_NUMBER)

    return review_result

def aggregate_reviews(reviews_list):
    """聚合所有文件的审查结果"""
    if not reviews_list:
        return "🤖 **AI Code Review**\n\n✅ 本次 PR 未包含可审查的代码文件（已跳过 .md/.txt 等非代码文件）。"
    
    aggregated_review = "🤖 **AI Code Review**\n\n"
    aggregated_review += "以下是针对各个文件的代码审查意见：\n\n"
    
    for i, (filename, review) in enumerate(reviews_list, 1):
        if review and review.strip():
            # 移除原有的标记头，因为我们会在汇总中添加
            clean_review = review.replace("🤖 **AI Code Review (by Qwen)**\n\n", "").strip()
            aggregated_review += f"### 文件: `{filename}`\n{clean_review}\n\n"
        else:
            aggregated_review += f"### 文件: `{filename}`\n✅ 该文件未发现问题\n\n"
    
    return aggregated_review

def post_or_update_comment(repo_full_name, pr_number, headers, review_body, comment_marker):
    """发布或更新评论"""
    # 检查是否已有 AI 评论
    existing_comment_id = get_existing_ai_comment_id(repo_full_name, pr_number, headers, comment_marker)
    
    # 确保 body 不为空、不只含空白
    if not review_body or not review_body.strip():
        review_body = "🤖 **AI Code Review**\n\n⚠️ 无法生成审查意见（内容为空或仅包含空白字符）。请检查 PR 变更或重试。"
    else:
        review_body = review_body.strip()  # 清理首尾空白
    
    if existing_comment_id:
        logger.info("🔄 已存在 AI 评论，正在更新...")
        # 直接更新旧评论（避免刷屏）
        update_url = f"https://api.github.com/repos/{repo_full_name}/issues/comments/{existing_comment_id}"
        
        try:
            update_resp = httpx.patch(update_url, headers=headers, json={"body": review_body}, timeout=HTTP_TIMEOUT)
            if update_resp.status_code == 200:
                logger.info("✅ AI 评论已更新！")
            else:
                logger.error(f"❌ 更新失败: {update_resp.text}")
        except httpx.RequestError as e:
            logger.error(f"更新评论时发生错误: {e}")
    else:
        logger.info("🆕 未发现已有 AI 评论，正在创建新评论...")
        comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        
        try:
            post_resp = httpx.post(comment_url, headers=headers, json={"body": review_body}, timeout=30.0)
            if post_resp.status_code in (200, 201):
                logger.info("✅ AI 评论已成功发布！")
            else:
                logger.error(f"❌ 发布评论失败: {post_resp.text}")
        except httpx.RequestError as e:
            logger.error(f"发布评论时发生错误: {e}")

def main():
    config = read_toml("config.toml")
    if config is None:
        logger.error("无法加载配置文件，程序退出")
        return
    # 常见代码文件扩展名（可按需扩展）
    CODE_EXTENSIONS = config['api']['CODE_EXTENSIONS']

    headers = {"Authorization": f"Bearer {config['api']['GITHUB_TOKEN']}", "Accept": "application/vnd.github.v3+json"}

    logger.info(f"🔍 正在分析 PR #{config['api']['PR_NUMBER']} 的变更文件...")

    files = get_pr_files(config['api']['REPO_FULL_NAME'], config['api']['PR_NUMBER'], headers)
    if files is None:
        logger.error("无法获取PR文件列表，程序退出")
        return

    filtered_patches = filter_code_patches(files,CODE_EXTENSIONS)
    agent = Model()
    if not filtered_patches:
        review_comment = "🤖 **AI Code Review**\n\n✅ 本次 PR 未包含可审查的代码文件（已跳过 .md/.txt 等非代码文件）。"
        post_or_update_comment(
            config['api']['REPO_FULL_NAME'], 
            config['api']['PR_NUMBER'], 
            headers, 
            review_comment, 
            config['api']['COMMENT_MARKER']
        )
    else:
        # 对每个文件单独进行代码审查
        reviews_list = []
        
        for file_info in filtered_patches:
            filename = file_info["filename"]
            patch = file_info["patch"]
            logger.debug(f"正在处理文件: {filename}")
            # 将宽泛的异常处理改为具体类型
            try:
                review = process_single_file(filename, patch, config['api']['PR_NUMBER'], agent)   
                reviews_list.append((filename, review))
            except httpx.RequestError as e:
                logger.error(f"处理文件 {filename} 时网络请求失败: {e}")
                reviews_list.append((filename, f"❌ 网络请求失败: {str(e)}"))
            except Exception as e:
                logger.error(f"处理文件 {filename} 时发生未知错误: {e}")
                reviews_list.append((filename, f"❌ 处理此文件时发生错误: {str(e)}"))
        
        # 汇总所有审查结果
        aggregated_review = aggregate_reviews(reviews_list)
        
        # 发布或更新评论
        post_or_update_comment(
            config['api']['REPO_FULL_NAME'], 
            config['api']['PR_NUMBER'], 
            headers, 
            aggregated_review, 
            config['api']['COMMENT_MARKER']
        )

if __name__ == "__main__":
    main()