import json
import os
import os.path
from typing import Any, Dict, List, Optional

import requests
import tomli

from app.tool.search.base import WebSearchEngine


class SerperSearchEngine(WebSearchEngine):
    """
    Serper搜索引擎实现，通过Serper API进行网络搜索
    """

    def __init__(self):
        # 尝试从配置文件读取设置
        config = {}
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config', 'config.toml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'rb') as f:  # 注意：tomli需要以二进制模式打开文件
                    config = tomli.load(f)
            except Exception as e:
                print(f"读取配置文件错误: {str(e)}")

        # 从配置文件或环境变量获取API密钥
        serper_config = config.get('search', {}).get('serper', {})
        self.api_key = serper_config.get('api_key') or os.environ.get("SERPER_API_KEY", "")
        self.default_gl = serper_config.get('default_gl', 'us')
        self.default_hl = serper_config.get('default_hl', 'en')

        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        # 日志记录初始化
        print(f"Serper搜索引擎初始化成功, API Key长度: {len(self.api_key)}")

    def perform_search(self, query: str, num_results: int = 10, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        通过Serper API执行搜索并返回结果

        Args:
            query (str): 搜索查询
            num_results (int, optional): 返回结果数量，默认为10

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 检查API密钥是否设置
        if not self.api_key:
            print("错误: Serper API密钥未设置，请在config.toml或环境变量中设置")
            return []

        gl = kwargs.get("gl", self.default_gl)  # 国家代码
        hl = kwargs.get("hl", self.default_hl)  # 语言

        payload = {
            "q": query,
            "gl": gl,
            "hl": hl,
            "autocorrect": True,
            "page": 1,
            "num": num_results,
            "type": "search"
        }

        print(f"Serper搜索: 查询='{query}', 国家='{gl}', 语言='{hl}', 结果数={num_results}")

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            search_results = response.json()

            print(f"Serper搜索成功: 收到{len(search_results.get('organic', []))}个有机结果")

            # 处理并整理结果
            results = []

            # 添加知识图谱结果（如果存在）
            if "knowledgeGraph" in search_results:
                kg = search_results["knowledgeGraph"]
                results.append({
                    "title": kg.get("title", ""),
                    "link": kg.get("website", ""),
                    "snippet": kg.get("description", ""),
                    "source": "知识图谱",
                    "attributes": kg.get("attributes", {})
                })

            # 添加有机搜索结果
            if "organic" in search_results:
                for item in search_results["organic"]:
                    result = {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "有机搜索",
                        "position": item.get("position", 0)
                    }

                    # 添加属性（如果存在）
                    if "attributes" in item:
                        result["attributes"] = item["attributes"]

                    # 添加站点链接（如果存在）
                    if "sitelinks" in item:
                        result["sitelinks"] = item["sitelinks"]

                    results.append(result)

            # 添加"人们也问"结果
            if "peopleAlsoAsk" in search_results:
                for item in search_results["peopleAlsoAsk"]:
                    results.append({
                        "title": item.get("question", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "人们也问"
                    })

            # 添加相关搜索
            if "relatedSearches" in search_results:
                for item in search_results["relatedSearches"]:
                    results.append({
                        "title": item.get("query", ""),
                        "link": f"https://www.google.com/search?q={item.get('query', '').replace(' ', '+')}",
                        "snippet": f"相关搜索: {item.get('query', '')}",
                        "source": "相关搜索"
                    })

            return results[:num_results]  # 确保不超过请求的结果数量

        except Exception as e:
            print(f"Serper搜索错误: {str(e)}")
            return []
