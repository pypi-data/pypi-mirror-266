"""
request请求工具
"""
import re
from typing import Mapping

from afeng_tools.http_tool import http_request_tools


def is_mobile(user_agent: str) -> bool:
    """判断是否是手机"""
    return http_request_tools.is_mobile(user_agent)


def is_json(headers: dict | Mapping) -> bool:
    """是否是json请求"""
    return http_request_tools.is_json(headers)

