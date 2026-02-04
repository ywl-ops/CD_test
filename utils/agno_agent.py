"""
Author: ywl-ops 2644984438@qq.com
Date: 2026-02-04
LastEditors: ywl-ops 2644984438@qq.com
LastEditTime: 2026-02-04
FilePath: /test/utils/agno_agent.py
Description: 
"""

from pydantic import BaseModel, Field
from agno.agent import Agent,RunOutput
from agno.models.openai import OpenAILike
from agno.run.base import RunStatus
from agno.team import Team
from pathlib import Path
import sys

parent_directory = Path(__file__).parent.parent
sys.path.append(str(parent_directory))  # 注意需要转换为字符串
from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams,SSEClientParams
from agno.skills import Skills, LocalSkills
from read_toml import read_toml
from loguru import logger
class Model:
    def __init__(self):
        config = read_toml("config.toml")
        self.model = OpenAILike(
            id="qwen3-coder-plus",
            api_key=config["api"]["DASHSCOPE_API_KEY"],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        prompt = """
            你是一位资深软件工程师，请对以下代码变更进行审查。你有codereview的节能,如果需要,可以进行加载技能。
            关注：
            - 潜在 bug（空指针、越界、资源泄漏等）
            - 安全风险（硬编码密钥、SQL 注入等）
            - 代码风格、可读性、可维护性
            - 性能问题
            - 是否符合最佳实践

            请用中文回答，每条意见以"\\n- [类型] 描述"格式列出。若无问题，回复"✅ 未发现明显问题
        """
        prompt = """
            你是一位资深软件工程师，你有代码审查的技能,如果需要,可以进行加载技能。
        """
        self.agent_James = Agent(
            model=self.model,
            instructions=prompt,
            markdown=True,
            skills=Skills(loaders=[LocalSkills(r"E:\data\python_project\test\codereviewskill")])
        )
    def generate_code_review(self, single_file_diff: str,PR_number:int):
        response:RunOutput = self.agent_James.run(f"请进行codereview,以下是变更的代码文件:{single_file_diff}")
        for message in response.messages:
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    logger.debug(f"Tool: {tool_call}")  # 会显示 get_skill_instructions 等调用
        if response.status == RunStatus.completed:
            return response.content
        else:
            return "生成代码review失败"