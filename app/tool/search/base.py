from typing import List, Optional

from pydantic import BaseModel, Field


# 数据模型；搜索返回结构体
class SearchItem(BaseModel):
    """Represents a single search result item"""

    title: str = Field(description="The title of the search result")
    url: str = Field(description="The URL of the search result")
    description: Optional[str] = Field(
        default=None, description="A description or snippet of the search result"
    )

    def __str__(self) -> str:
        """String representation of a search result item."""
        return f"{self.title} - {self.url}"

# 抽象基类；搜索引擎基类
class WebSearchEngine(BaseModel):
    """Base class for web search engines."""

    model_config = {"arbitrary_types_allowed": True}

    def perform_search(
        self, query: str, num_results: int = 10, *args, **kwargs
    ) -> List[SearchItem]: # 返回搜索结果列表
        """
        Perform a web search and return a list of search items.

        Args:
            query (str): The search query to submit to the search engine. # 搜索查询
            num_results (int, optional): The number of search results to return. Default is 10. # 搜索结果数量
            args: Additional arguments. # 额外参数
            kwargs: Additional keyword arguments. # 额外关键字参数

        Returns:
            List[SearchItem]: A list of SearchItem objects matching the search query. # 返回搜索结果列表
        """
        raise NotImplementedError # 未实现错误
