import os.path

from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates, _TemplateResponse

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.fastapi_tool.fastapi_request_tools import generate_request_id
from afeng_tools.file_tool import tmp_file_tools

jinja2_templates = Jinja2Templates(directory=settings_tools.get_config(SettingsKeyEnum.server_template_path))


def create_template_response(request: Request, template_file: str, context: dict = None, is_cache=False,
                             cache_path: str = None) -> _TemplateResponse:
    """
    创建模板响应
    :param request: Request
    :param template_file: 模板文件
    :param context: 上下文内容
    :param is_cache:
    :param cache_path:
    :return:
    """
    if isinstance(context, Response):
        return context
    if not context:
        context = dict()
    if 'request' not in context:
        context['request'] = request
    response = jinja2_templates.TemplateResponse(template_file, context=context)
    if is_cache:
        if cache_path is None:
            cache_path = tmp_file_tools.get_user_tmp_dir()
        else:
            os.makedirs(cache_path, exist_ok=True)
        unique_id = generate_request_id(request)
        with open(os.path.join(cache_path, f'{unique_id}.html'), 'wb') as f:
            f.write(response.body)
    return response
