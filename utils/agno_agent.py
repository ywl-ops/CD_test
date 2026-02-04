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
from loguru import logger

parent_directory = Path(__file__).parent.parent
sys.path.append(str(parent_directory))  # 注意需要转换为字符串
from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams,SSEClientParams
from agno.skills import Skills, LocalSkills
from read_toml import read_toml
from loguru import logger
from agno.workflow import Step, Workflow
from agno.workflow.types import StepInput,StepOutput
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
            你是一位资深软件工程师，你有代码审查的技能,如果需要,可以进行加载技能.
        """
        prompt_summary = """
            你是一位资深软件工程师，请对以下代码评审进行总结,对每个文件给出修改功能总结,对于问题,仅汇总高风险的问题,对于每个文件需要改进的地方,给出改进建议的代码。
        """
        self.agent_James = Agent(
            model=self.model,
            instructions=prompt,
            markdown=True,
            skills=Skills(loaders=[LocalSkills(r"E:\data\python_project\test\codereviewskill")])
        )
        self.agent_summary = Agent(
            model=self.model,
            instructions=prompt_summary,
            markdown=True,
        )
        # 创建 Workflow
        self.workflow = Workflow(
            name="代码审查流程",
            steps=[
                Step(name="Code Review", executor=self.review_multiple_files),
                Step(name="Summary", agent=self.agent_summary),
            ]
        )

    def review_multiple_files(self,step_input: StepInput) -> StepOutput:
        """让 James 审查多份代码文件"""
        files = step_input.input  # 传入的代码文件列表
        
        all_reviews = []
        for i, (filename,file_diff) in enumerate(files):
            logger.debug(f"正在处理文件: {filename}")
            response = self.agent_James.run(f"请进行codereview,以下是变更的代码文件:{file_diff}")
            all_reviews.append(f"## 文件:{filename} {i+1} 审查结果:\n{response.content}")
        
        # 合并所有审查结果
        combined_reviews = "\n\n".join(all_reviews)
        return StepOutput(content=combined_reviews, success=True)
    # 使用方式
    def generate_code_review(self, file_diffs: list):
        response = self.workflow.run(input=file_diffs)
        return response.content