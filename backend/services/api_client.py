"""外部 API 调用封装 — 自动重试 + 降级。

设计思路：
    所有外部 HTTP 调用统一走 safe_get()，自动处理：
    1. 指数退避重试（1s → 2s → 4s）
    2. 超时保护
    3. 失败时返回 fallback 值而非抛异常

    这样 Agent 不会因为一个工具调用失败就崩溃，
    LLM 仍然可以基于自身知识给出建议。
"""

import time
import logging
import requests as http

logger = logging.getLogger("travel-agent")

MAX_RETRIES = 2
RETRY_DELAYS = [1, 2]


def safe_get(url: str, params: dict = None, timeout: int = 8,
             fallback=None, retries: int = MAX_RETRIES) -> http.Response | None:
    """带重试的 HTTP GET 请求。

    Args:
        url: 请求地址
        params: 查询参数
        timeout: 超时秒数
        fallback: 全部重试失败后返回的降级值
        retries: 最大重试次数
    """
    for attempt in range(retries + 1):
        try:
            resp = http.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except http.exceptions.Timeout:
            logger.warning(f"API 请求超时 (attempt {attempt + 1}): {url}")
        except http.exceptions.ConnectionError:
            logger.warning(f"API 连接失败 (attempt {attempt + 1}): {url}")
        except http.exceptions.HTTPError as e:
            logger.warning(f"API 返回错误 (attempt {attempt + 1}): {e}")
        except Exception as e:
            logger.warning(f"API 请求异常 (attempt {attempt + 1}): {e}")

        if attempt < retries:
            delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
            logger.info(f"等待 {delay}s 后重试...")
            time.sleep(delay)

    logger.error(f"API 请求最终失败，使用降级数据: {url}")
    return fallback
