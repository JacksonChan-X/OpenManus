"""工具选择指南提示词。"""

TOOL_SELECTION_GUIDE = """
# OpenManus 工具选择指南

请根据用户的请求类型选择最合适的工具：

## 搜索和信息获取类任务
- 使用 `web_search` 工具直接进行网络搜索
  - 示例: web_search(query="最新AI技术发展")
  - 适用场景: 查找事实信息、新闻、最新发展等

## 网页浏览和交互
- 使用 `browser_use` 工具进行网页浏览和交互
  - 示例: browser_use(action="go_to_url", url="https://example.com")
  - 适用场景: 访问网站、点击按钮、填写表单、提取网页内容

## 文件和代码操作
- 使用 `python_execute` 工具执行Python代码
  - 示例: python_execute(code="import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())")
  - 适用场景: 数据处理、文件操作、编程任务

## 数学计算
- 使用 `calculator` 工具进行复杂数学计算
  - 示例: calculator(expression="(2 + 3) * 4 / 2")
  - 适用场景: 需要精确计算结果的场合

## 任务完成
- 完成全部任务后使用 `terminate` 工具结束流程
  - 示例: terminate(reason="Task completed successfully")

关键原则:
1. 始终选择一个工具而不是仅仅描述计划
2. 选择最直接解决问题的工具，避免不必要的规划
3. 复杂任务分解为多个简单步骤，每步使用最合适的工具
4. 搜索相关任务必须立即使用搜索工具，不要过度规划
"""

def get_tool_selection_prompt(message: str) -> str:
    """
    基于用户消息生成工具选择提示。

    Args:
        message: 用户的消息内容

    Returns:
        工具选择提示字符串
    """
    # 分析消息中的关键词来确定可能的工具,若命中关键词则将对应工具添加到列表中以便后续选择使用
    search_keywords = ["搜索", "查找", "了解", "信息", "寻找", "search", "find", "look up"]
    browser_keywords = ["网站", "网页", "浏览", "访问", "网址", "url", "website", "browser"]
    code_keywords = ["代码", "编程", "运行", "执行", "计算", "code", "program", "execute", "calculate"]
    file_keywords = ["文件", "保存", "读取", "表格", "file", "save", "read", "excel"]

    suggested_tools = []

    if any(kw in message.lower() for kw in search_keywords):
        suggested_tools.append("web_search")

    if any(kw in message.lower() for kw in browser_keywords):
        suggested_tools.append("browser_use")

    if any(kw in message.lower() for kw in code_keywords):
        suggested_tools.append("python_execute")

    if any(kw in message.lower() for kw in file_keywords):
        suggested_tools.append("python_execute")

    # 如果没有明确的工具建议，建议使用web_search作为首选
    if not suggested_tools:
        suggested_tools.append("web_search")

    # 构建特定的工具提示
    tool_prompt = f"""
    基于您的请求: "{message[:100]}{'...' if len(message) > 100 else ''}"

    建议的工具: {', '.join(suggested_tools)}

    请立即使用上述工具之一执行具体操作，而不是继续规划。
    """

    return TOOL_SELECTION_GUIDE + "\n" + tool_prompt
