import os
import re
import time
import typing
from abc import ABCMeta, abstractmethod, ABC

from starlette.middleware.base import _StreamingResponse
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, StreamingResponse

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.cache_tool import cache_memory_tools
from afeng_tools.fastapi_tool.fastapi_request_tools import generate_request_id
from afeng_tools.file_tool import tmp_file_tools
from afeng_tools.file_tool.file_tools import iterate_read_file


def request_set_no_cache(request: Request):
    request.scope['request_not_cache'] = True


class HttpCacher(metaclass=ABCMeta):
    def __init__(self, request: Request, app_info: AppInfo):
        self.request = request
        self.request_id = generate_request_id(request)
        self.app_info = app_info

    @abstractmethod
    def is_need_cache(self) -> bool:
        """是否需要缓存"""
        return False

    @abstractmethod
    def remove_cache(self):
        """移除缓存"""
        pass

    @abstractmethod
    def get_cache(self) -> tuple[bool, Response | None]:
        """
        获取缓存
        :return: （是否有缓存，缓存响应）
        """
        return False, None

    @abstractmethod
    async def save_cache(self, response: Response) -> Response | None:
        """
        保存缓存
        :param response: 响应内容
        :return: 如果返回None，则使用原response; 如果返回Response, 则响应Response
        """
        pass


class HttpRedirectCacher(HttpCacher, ABC):

    def is_need_cache(self) -> bool:
        """是否需要缓存"""
        return True

    def remove_cache(self):
        """移除缓存"""
        cache_memory_tools.delete_cache('redirect_cache', self.request_id)

    def get_cache(self) -> tuple[bool, Response | None]:
        cache_info = cache_memory_tools.get_time_cache('redirect_cache', self.request_id)
        if cache_info:
            cache_time, redirect_url = cache_info
            re_search = re.search('&(time|dstime)=(.*?)&', redirect_url)
            if re_search and time.time() >= (cache_time + 8 * 3600 - 100):
                cache_memory_tools.delete_cache('redirect_cache', self.request_id)
                return False, None
            return True, RedirectResponse(redirect_url)
        return False, None

    async def save_cache(self, response: Response):
        if response.status_code == 307:
            redirect_url = response.headers.get('location')
            re_search = re.search('&(time|dstime)=(.*?)&', redirect_url)
            if re_search:
                timestamp = float(re_search.group(2))
            else:
                timestamp = time.time()
            cache_memory_tools.add_time_cache('redirect_cache', self.request_id, redirect_url, timestamp=timestamp)


class HttpHtmlCacher(HttpCacher, ABC):

    def __init__(self, request: Request, app_info: AppInfo):
        super().__init__(request, app_info)
        self.request_cache_file = self._get_request_cache_file()

    def _get_request_cache_file(self) -> str:
        if self.app_info:
            save_child_path = self.request.url.path.removeprefix(f'{self.app_info.prefix}/')
            return str(os.path.join(settings_tools.get_config('server.html_save_path'),
                                    self.app_info.code, 'cache', save_child_path, f'{self.request_id}.html'))
        else:
            save_child_path = self.request.url.path.removeprefix('/')
            return str(os.path.join(tmp_file_tools.get_user_tmp_dir(),
                                    'html_cache', save_child_path, f'{self.request_id}.html'))

    async def _request_save_cache(self, body_iterator: typing.AsyncIterable, charset: str, is_gzip=False):
        cache_file = self.request_cache_file
        if is_gzip:
            cache_file = cache_file + '.gzip'
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'wb') as f:
            async for chunk in body_iterator:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(charset)
                f.write(chunk)

    def is_need_cache(self) -> bool:
        """是否需要缓存"""
        return self.request.headers and self.request.headers.get('accept') and 'html' in self.request.headers.get(
            'accept')

    def remove_cache(self, is_gzip=False):
        """移除缓存"""
        cache_file = self.request_cache_file
        if is_gzip:
            cache_file = cache_file + '.gzip'
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def get_cache(self) -> tuple[bool, Response | None]:
        """
        获取缓存
        :return: （是否有缓存，缓存响应）
        """
        if os.path.exists(self.request_cache_file):
            return True, StreamingResponse(content=iterate_read_file(self.request_cache_file, binary_flag=True),
                                           media_type="text/html")
        gzip_cache_html = self.request_cache_file + '.gzip'
        if os.path.exists(gzip_cache_html):
            return True, StreamingResponse(content=iterate_read_file(gzip_cache_html, binary_flag=True),
                                           headers={'content-length': str(os.stat(gzip_cache_html).st_size),
                                                    'content-type': 'text/html; charset=utf-8',
                                                    'content-encoding': 'gzip',
                                                    'vary': 'Accept-Encoding'})
        return False, None

    async def save_cache(self, response: Response):
        if response.status_code == 200 and response.headers.get('content-type') and response.headers.get(
                'content-type').startswith('text/html'):
            if isinstance(response, _StreamingResponse):
                await self._request_save_cache(response.body_iterator, response.charset,
                                               is_gzip=response.headers.get('content-encoding') == 'gzip')
                has_cache, resp = self.get_cache()
                return resp
