from typing import Type

from afeng_tools.encryption_tool import hashlib_tools
from pydantic import BaseModel
from starlette.datastructures import FormData
from starlette.requests import Request

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.convert_tool.type_convert_tools import convert_value_to_type
from afeng_tools.http_tool import http_request_tools


def generate_request_id(request: Request) -> str:
    """生成request的唯一id"""
    return hashlib_tools.calc_unique_id(data_list=[
        http_request_tools.is_mobile(request.headers.get('user-agent')),
        request.method,
        request.url,
        request.query_params,
    ], split_chat='||')


def form_params_convert_to_model(form_model_class: Type[BaseModel]):
    """将表单参数转换为pydantic的Model对象"""

    async def func_wrap(request: Request):
        body = await request.form()
        if body:
            model_value_dict = dict()
            field_dict = form_model_class.model_fields
            for tmp_key, tmp_value in body.items():
                if tmp_key in field_dict:
                    model_value_dict[tmp_key] = convert_value_to_type(tmp_value, field_dict.get(tmp_key).annotation)
            return form_model_class(**model_value_dict)

    return func_wrap


async def do_handle_form_array_item(form_data: FormData) -> FormData:
    """处理form表单提交的数组"""
    new_form_data_list = []
    for tmp_key in form_data.keys():
        if tmp_key.endswith('[]'):
            new_form_data_list.append((tmp_key.removesuffix('[]'), form_data.getlist(tmp_key)))
        else:
            new_form_data_list.append((tmp_key, form_data.get(tmp_key)))
    return FormData(new_form_data_list)


def get_request_app_info(request: Request, app_dict: dict[str, AppInfo]) -> AppInfo:
    """获取请求的AppInfo"""
    if hasattr(request, 'scope') and request.scope:
        app_info = request.scope.get('app_info')
        if app_info:
            return app_info
    request_path = request.url.path
    for app_info in app_dict.values():
        if request_path.startswith(app_info.prefix + '/'):
            request.scope['app_info'] = app_info
            return app_info
