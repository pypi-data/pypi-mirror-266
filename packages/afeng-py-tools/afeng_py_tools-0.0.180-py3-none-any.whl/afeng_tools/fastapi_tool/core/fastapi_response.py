from typing import Sequence, Any

from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.core.fastapi_items import ResponseResult, ResponseTemplateResult


def json_resp(error_no: int = 0, message: str | Sequence = 'success',
              sub_message: str = None,
              data: Any = None,
              http_status: int = 200) -> JSONResponse:
    """json响应"""
    return JSONResponse(
        status_code=http_status,
        content=jsonable_encoder(ResponseResult(error_no=error_no,
                                                message=message, sub_message=sub_message, data=data)),
    )


def template_resp(request: Request, resp_result: ResponseTemplateResult, app_info: AppInfo = None) -> Response:
    """模板响应"""
    context_data = resp_result.context_data
    if context_data is None:
        context_data = dict()
    if 'app_info' not in context_data:
        context_data['app_info'] = app_info
    if 'title' not in context_data:
        context_data['title'] = resp_result.title
    if 'message' not in context_data:
        context_data['message'] = resp_result.message
    from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response
    return create_template_response(request=request,
                                    template_file=resp_result.template_file,
                                    context=context_data)
