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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# ===== 你要修改的部分 =====
REPO_FULL_NAME = "yourname/my-repo"  # 替换成你的仓库，如 "alibaba/Qwen"
PR_NUMBER = 42                      # 替换成你的 PR 编号
# =========================

# GitHub API 请求头
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

print(f"正在获取 PR #{PR_NUMBER} 的 diff...")

# 1. 获取 PR 的 diff
response = httpx.get(
    f"https://api.github.com/repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}",
    headers=headers
)

if response.status_code != 200:
    print("❌ 获取 diff 失败:", response.text)
    exit(1)

diff_content = response.text
print("✅ 成功获取 diff，长度:", len(diff_content), "字符")

# 如果 diff 太大，可以截断（Qwen 有上下文限制）
MAX_DIFF_LENGTH = 12000  # qwen-max 上下文约 3 万字，留点余量
if len(diff_content) > MAX_DIFF_LENGTH:
    diff_content = diff_content[:MAX_DIFF_LENGTH]
    print("⚠️ diff 过长，已截断至", MAX_DIFF_LENGTH, "字符")

# 2. 调用 Qwen 进行 Code Review
prompt = f"""
你是一位资深软件工程师，请对以下 Git diff 进行代码审查。关注：
- 潜在 bug（空指针、越界、资源泄漏等）
- 安全风险（硬编码密钥、SQL 注入等）
- 代码风格、可读性、可维护性
- 性能问题
- 是否符合最佳实践

请用中文回答，每条意见以“- [类型] 描述”格式列出。若无问题，回复“✅ 未发现明显问题”。

以下是本次 PR 的代码变更（diff 格式）：

{diff_content}
"""

print("\n正在调用 Qwen 进行 Code Review...")

qwen_response = httpx.post(
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    headers={
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "qwen-max",  # 也可用 qwen-plus（性价比高）
        "input": {
            "messages": [{"role": "user", "content": prompt}]
        },
        "parameters": {"result_format": "message"}
    },
    timeout=60.0
)

if qwen_response.status_code != 200:
    print("❌ Qwen 调用失败:", qwen_response.text)
    exit(1)

# 3. 解析并输出结果
review_result = qwen_response.json()["output"]["choices"][0]["message"]["content"]
print("\n" + "="*50)
print("🤖 Qwen Code Review 结果:")
print("="*50)
print(review_result)