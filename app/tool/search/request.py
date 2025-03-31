from typing import Tuple

import requests

from app.logger import logger


class RequestHandler:
    """处理网络请求的工具类"""

    @staticmethod
    def handle_redirect(url: str, max_redirects: int = 5, timeout: int = 10) -> Tuple[str, bool]:
        """
        处理URL重定向，返回最终URL

        Args:
            url (str): 初始URL
            max_redirects (int): 最大重定向次数，默认5次
            timeout (int): 超时时间，默认10秒

        Returns:
            Tuple[str, bool]: (最终URL, 是否发生了重定向)
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            # 使用HEAD请求检查重定向
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=timeout,
                headers=headers,
                max_redirects=max_redirects
            )

            final_url = response.url
            is_redirected = len(response.history) > 0

            if is_redirected:
                logger.debug(f"URL重定向: {url} -> {final_url}")

            return final_url, is_redirected

        except requests.TooManyRedirects:
            logger.warning(f"重定向次数过多: {url}")
            return url, False

        except requests.Timeout:
            logger.warning(f"请求超时: {url}")
            return url, False

        except Exception as e:
            logger.warning(f"处理重定向时出错: {url}, 错误: {str(e)}")
            return url, False

    @staticmethod
    def get_with_redirect(url: str, **kwargs) -> requests.Response:
        """
        发送GET请求并处理重定向

        Args:
            url (str): 请求URL
            **kwargs: requests.get的其他参数

        Returns:
            requests.Response: 响应对象
        """
        final_url, _ = RequestHandler.handle_redirect(url)
        return requests.get(final_url, **kwargs)

# 实现重定向

r = requests.get("https://www.baidu.com")


print(r.status_code)
print(r.text)
