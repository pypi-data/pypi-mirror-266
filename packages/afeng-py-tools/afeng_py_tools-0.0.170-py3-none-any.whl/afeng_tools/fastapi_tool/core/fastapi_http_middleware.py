from datetime import datetime
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from afeng_tools.fastapi_tool.core.fastapi_http_cacher import HttpCacher


class FastapiHttpMiddleware:
    def __init__(self, request: Request, async_next_callback: Callable[[Request, ], Response],
                 http_cacher_chain: list[HttpCacher],
                 is_debug: bool = False,
                 has_before_print: bool = True, is_cache: bool = False):
        self.request = request
        self.async_next_callback = async_next_callback
        self.is_debug = is_debug
        self.has_before_print = has_before_print
        self.is_cache = is_cache
        self.http_cacher_chain = http_cacher_chain
        self.response = None

    def before_print(self):
        """响应前输出"""
        real_ip = ''
        if self.request.headers:
            real_ip = self.request.headers.get('X-Real-IP')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"[{current_time}][{real_ip}-{self.request.method}]{self.request.url}")

    def is_in_blacklist(self) -> bool:
        """是否在黑名单中"""
        return False

    @classmethod
    def resp_forbidden(cls, http_status: int = 403) -> Response:
        """响应禁止"""
        return PlainTextResponse('Access denied', status_code=http_status)

    async def resp(self):
        """响应"""
        return await self.async_next_callback(self.request)

    async def run(self) -> Response:
        """运行中间件拦截"""
        if self.has_before_print:
            self.before_print()
        # 是否不是调试
        if not self.is_debug:
            # 是否在黑名单中
            if self.is_in_blacklist():
                return self.resp_forbidden()
            # 是否缓存
            if self.is_cache:
                for tmp_http_cacher in self.http_cacher_chain:
                    if tmp_http_cacher.is_need_cache():
                        has_cache, cache_response = tmp_http_cacher.get_cache()
                        if has_cache:
                            return cache_response

                self.response = await self.resp()
                if not self.request.scope.get('request_not_cache'):
                    for tmp_http_cacher in self.http_cacher_chain:
                        resp = await tmp_http_cacher.save_cache(self.response)
                        if resp:
                            return resp
                return self.response
        return await self.resp()