from typing import Optional

from pydantic import Field, model_validator

from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor


class Manus(ToolCallAgent):
    """A versatile general-purpose agent."""

    name: str = "Manus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000  # 观察次数
    max_steps: int = 20  # 最大步骤

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection( # 抽象出工具集合
            PythonExecute(), BrowserUseTool(), StrReplaceEditor(), Terminate() # 工具集合: 执行python代码, 使用浏览器, 替换字符串, 终止
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    browser_context_helper: Optional[BrowserContextHelper] = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "Manus":
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        # Store original prompt
        original_prompt = self.next_step_prompt # 存储原始提示

        # 检查是否多次没有选择工具
        no_tool_count = 0
        for i in range(min(5, len(self.memory.messages))):
            if i >= len(self.memory.messages):
                break
            msg = self.memory.messages[-(i+1)]
            if msg.role == "assistant" and not getattr(msg, "tool_calls", None):
                no_tool_count += 1
            else:
                break

        # 如果连续多次没有选择工具，添加更强的提示
        if no_tool_count >= 1:
            tool_names = [tool.name for tool in self.available_tools.tools]
            # 构建更直接的提示,列举可以使用的工具，提示立即使用工具
            action_prompt = f"""
CRITICAL INSTRUCTION: You MUST use a tool now instead of just planning.

Available tools: {', '.join(tool_names)}

Based on the conversation history,
You should immediately use one of these tools to make progress.

SELECT A TOOL NOW AND TAKE ACTION.
"""
            self.next_step_prompt = action_prompt + "\n" + original_prompt

        # Only check recent messages (last 3) for browser activity
        recent_messages = self.memory.messages[-3:] if self.memory.messages else [] # 获取最近的消息
        browser_in_use = any(
            "browser_use" in msg.content.lower() # 检查消息内容是否包含"browser_use"
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use:
            # Override with browser-specific prompt temporarily to get browser context
            self.next_step_prompt = BROWSER_NEXT_STEP_PROMPT # 如果检测到正在使用浏览器则使用浏览器特定的提示

        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result

    async def cleanup(self):
        """Clean up Manus agent resources."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
