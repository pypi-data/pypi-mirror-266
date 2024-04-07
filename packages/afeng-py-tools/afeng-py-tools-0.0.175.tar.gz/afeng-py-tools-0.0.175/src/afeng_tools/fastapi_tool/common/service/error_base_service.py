import os.path
from abc import ABCMeta, abstractmethod

from starlette.requests import Request

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.core.fastapi_response import json_resp
from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response
from afeng_tools.fastapi_tool.template.item import Error501DataItem, Error500DataItem, Error404DataItem, \
    TemplateError404AreaData, TemplateError501AreaData, TemplateError500AreaData
from afeng_tools.fastapi_tool.template.service import template_render_service
from afeng_tools.http_tool import http_request_tools


class ErrorService(metaclass=ABCMeta):

    @abstractmethod
    def handle_404(self, error_data: Error404DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        return json_resp(error_no=404, message=error_data.message, sub_message=error_data.sub_message)

    @abstractmethod
    def handle_500(self, error_data: Error500DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        return json_resp(error_no=500, message=error_data.message, sub_message=error_data.sub_message)

    @abstractmethod
    def handle_501(self, error_data: Error501DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        return json_resp(error_no=501, message=error_data.message, sub_message=error_data.sub_message)


class DefaultErrorService(ErrorService):
    """默认错误处理"""

    def __init__(self, app_code: str = 'common'):
        self.app_code = app_code
        self.template_root_path = settings_tools.get_config(SettingsKeyEnum.server_template_path)

    def handle_response(self, request: Request,
                        error_no: int,
                        error_title: str,
                        error_data: Error404DataItem | Error500DataItem | Error501DataItem,
                        error_template_file: str = 'views/error/index.html',
                        context_data: dict = None,
                        app_info: AppInfo = None):
        if request and not http_request_tools.is_json(request.headers) and not (app_info and app_info.is_json_api):
            app_info = app_info if app_info else request.scope.get('app_info')
            if context_data and 'template_file' in context_data:
                error_index_template_file = context_data['template_file']
            else:
                error_index_template_file = f'{self.app_code}/{error_template_file}'
                if app_info:
                    if self.template_root_path:
                        if os.path.exists(
                                os.path.join(str(self.template_root_path), f'{app_info.code}/{error_template_file}')):
                            error_index_template_file = f'{app_info.code}/{error_template_file}'
            if os.path.exists(
                    os.path.join(str(self.template_root_path), error_index_template_file)):
                if context_data is None:
                    context_data = dict()
                if app_info and 'app_info' not in context_data:
                    context_data['app_info'] = app_info
                if 'is_mobile' not in context_data:
                    context_data['is_mobile'] = http_request_tools.is_mobile(request.headers.get('user-agent'))
                if 'title' not in context_data:
                    context_data['title'] = error_title
                if 'message' not in context_data:
                    context_data['message'] = error_data.message
                if 'sub_message' not in context_data:
                    context_data['sub_message'] = error_data.sub_message

                return create_template_response(request=request,
                                                template_file=error_index_template_file,
                                                context=context_data)
        return json_resp(error_no=error_no, message=error_data.message, sub_message=error_data.sub_message)

    def handle_404(self, error_data: Error404DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        if context_data is None:
            context_data = dict()
        is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
        if 'is_mobile' not in context_data:
            context_data['is_mobile'] = is_mobile
        if 'template_error_area' not in context_data:
            _error_area, _error_file = template_render_service.get_template_error_404_area(
                group_code='error/404',
                context_data_func=lambda: TemplateError404AreaData(is_mobile=is_mobile, **error_data.model_dump()),
                app_code=self.app_code,
                reload_freq=ReloadFreqEnum.always
            )
            context_data['template_error_area'] = _error_file
        return self.handle_response(request=request,
                                    error_no=404,
                                    error_title='404-Not Found',
                                    error_data=error_data,
                                    context_data=context_data,
                                    app_info=app_info)

    def handle_500(self, error_data: Error500DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        if context_data is None:
            context_data = dict()
        is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
        if 'is_mobile' not in context_data:
            context_data['is_mobile'] = is_mobile
        if 'template_error_area' not in context_data:
            _error_area, _error_file = template_render_service.get_template_error_500_area(
                group_code='error/500',
                context_data_func=lambda: TemplateError500AreaData(is_mobile=is_mobile, **error_data.model_dump()),
                app_code=self.app_code,
                reload_freq=ReloadFreqEnum.always
            )
            context_data['template_error_area'] = _error_file
        return self.handle_response(request=request,
                                    error_no=500,
                                    error_title='500-服务器错误',
                                    error_data=error_data,
                                    context_data=context_data,
                                    app_info=app_info)

    def handle_501(self, error_data: Error501DataItem, request: Request = None, context_data: dict = None,
                   app_info: AppInfo = None):
        if context_data is None:
            context_data = dict()
        is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
        if 'is_mobile' not in context_data:
            context_data['is_mobile'] = is_mobile
        if 'template_error_area' not in context_data:
            _error_area, _error_file = template_render_service.get_template_error_501_area(
                group_code='error/501',
                context_data_func=lambda: TemplateError501AreaData(is_mobile=is_mobile, **error_data.model_dump()),
                app_code=self.app_code,
                reload_freq=ReloadFreqEnum.always
            )
            context_data['template_error_area'] = _error_file
        return self.handle_response(request=request,
                                    error_no=501,
                                    error_title='501-操作失败',
                                    error_data=error_data,
                                    context_data=context_data,
                                    app_info=app_info)
