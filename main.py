"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/main.py
Description: 
"""
import os
import httpx
COMMENT_MARKER = "🤖 **AI Code Review"  # 用于识别是否已有 AI 评论

def get_existing_ai_comment_id(repo_full_name: str, pr_number: int) -> int | None:
    """检查是否存在 AI 评论，若存在返回 comment_id，否则返回 None"""
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    resp = httpx.get(url, headers=headers)
    if resp.status_code != 200:
        print("⚠️ 获取已有评论失败，跳过去重检查")
        return None

    comments = resp.json()
    for comment in comments:
        if COMMENT_MARKER in comment.get("body", ""):
            return comment["id"]  # 返回 comment_id
    return None

# 配置


# ===== 你要修改的部分 =====
REPO_FULL_NAME = "ywl-ops/CD_test"  # 替换成你的仓库，如 "alibaba/Qwen"
PR_NUMBER = 2                      # 替换成你的 PR 编号
# =========================

# 常见代码文件扩展名（可按需扩展）
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.cc', '.cxx',
    '.h', '.hpp', '.cs', '.rb', '.php', '.swift', '.kt', '.kts', '.scala', '.lua',
    '.pl', '.sh', '.bash', '.zsh', '.ps1', '.sql', '.yaml', '.yml', '.json', '.toml',
    '.xml', '.html', '.css', '.scss', '.less', '.proto', '.dockerfile'
}

headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

print(f"🔍 正在分析 PR #{PR_NUMBER} 的变更文件...")

# 1. 获取 PR 的所有变更文件
files_url = f"https://api.github.com/repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/files"
resp = httpx.get(files_url, headers=headers)
if resp.status_code != 200:
    print("❌ 获取文件列表失败:", resp.text)
    exit(1)

files = resp.json()
filtered_patches = []

for f in files:
    filename = f["filename"]
    status = f.get("status", "")
    patch = f.get("patch", "")

    # 跳过删除的文件
    if status == "removed":
        print(f"🗑️ 跳过已删除文件: {filename}")
        continue

    # 判断是否为代码文件
    _, ext = os.path.splitext(filename.lower())
    if ext not in CODE_EXTENSIONS:
        print(f"📄 跳过非代码文件: {filename}")
        continue

    if not patch.strip():
        print(f"EmptyEntries 跳过空变更文件: {filename}")
        continue

    filtered_patches.append(f"--- {filename} ---\n{patch}")

if not filtered_patches:
    review_comment = "🤖 **AI Code Review**\n\n✅ 本次 PR 未包含可审查的代码文件（已跳过 .md/.txt 等非代码文件）。"
else:
    full_diff = "\n\n".join(filtered_patches)
    
    # 截断过长内容（Qwen 上下文限制）
    if len(full_diff) > 12000:
        full_diff = full_diff[:12000] + "\n...（内容过长，已截断）"

prompt = f"""
    你是一位资深软件工程师，请对以下代码变更进行审查。关注：
    - 潜在 bug（空指针、越界、资源泄漏等）
    - 安全风险（硬编码密钥、SQL 注入等）
    - 代码风格、可读性、可维护性
    - 性能问题
    - 是否符合最佳实践

    请用中文回答，每条意见以“- [类型] 描述”格式列出。若无问题，回复“✅ 未发现明显问题”。

    以下是变更的代码文件：

    {full_diff}
"""

print("🧠 正在调用 Qwen 进行 Code Review...")
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

if qwen_resp.status_code != 200:
    print("❌ Qwen 调用失败:", qwen_resp.text)
    exit(1)

    review_text = qwen_resp.json()["output"]["choices"][0]["message"]["content"]
    review_body = f"{COMMENT_MARKER} (by Qwen)\n\n{review_text}"

# 3. 检查是否已有 AI 评论
existing_comment_id = get_existing_ai_comment_id(REPO_FULL_NAME, PR_NUMBER)

if existing_comment_id:
    print("🔄 已存在 AI 评论，正在更新...")
    # 方式一：【推荐】直接更新旧评论（避免刷屏）
    update_url = f"https://api.github.com/repos/{REPO_FULL_NAME}/comments/{existing_comment_id}"
    update_resp = httpx.patch(update_url, headers=headers, json={"body": review_body})
    if update_resp.status_code == 200:
        print("✅ AI 评论已更新！")
    else:
        print("❌ 更新失败:", update_resp.text)
else:
    print("🆕 未发现已有 AI 评论，正在创建新评论...")
    comment_url = f"https://api.github.com/repos/{REPO_FULL_NAME}/issues/{PR_NUMBER}/comments"
    post_resp = httpx.post(comment_url, headers=headers, json={"body": review_body})
    if post_resp.status_code in (200, 201):
        print("✅ AI 评论已成功发布！")
    else:
        print("❌ 发布评论失败:", post_resp.text)