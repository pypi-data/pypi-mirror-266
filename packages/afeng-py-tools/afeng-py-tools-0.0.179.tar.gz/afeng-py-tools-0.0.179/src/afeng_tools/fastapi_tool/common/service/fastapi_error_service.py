from starlette.requests import Request
from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.common.service.error_base_service import ErrorService
from afeng_tools.fastapi_tool.core.fastapi_response import json_resp
from afeng_tools.fastapi_tool.template.item import Error501DataItem, Error404DataItem, Error500DataItem
from afeng_tools.import_tool import import_tools


def _import_error_service(request: Request = None, app_info: AppInfo = None):
    app_info = app_info if app_info else (request.scope.get('app_info') if request else None)
    if app_info:
        if app_info.error_service_class:
            return import_tools.import_class(app_info.error_service_class)


def handle_404(error_data: Error404DataItem, request: Request = None, context_data: dict = None,
               app_info: AppInfo = None):
    Error_Service = _import_error_service(request=request, app_info=app_info)
    if Error_Service and issubclass(Error_Service, ErrorService):
        return Error_Service().handle_404(error_data=error_data, request=request, context_data=context_data,
                                          app_info=app_info)
    return json_resp(error_no=404, message=error_data.message, sub_message=error_data.sub_message)


def handle_500(error_data: Error500DataItem, request: Request = None, context_data: dict = None,
               app_info: AppInfo = None):
    Error_Service = _import_error_service(request=request, app_info=app_info)
    if Error_Service and issubclass(Error_Service, ErrorService):
        return Error_Service().handle_500(error_data=error_data, request=request, context_data=context_data,
                                          app_info=app_info)
    return json_resp(error_no=500, message=error_data.message, sub_message=error_data.sub_message)


def handle_501(error_data: Error501DataItem, request: Request = None, context_data: dict = None,
               app_info: AppInfo = None):
    Error_Service = _import_error_service(request=request, app_info=app_info)
    if Error_Service and issubclass(Error_Service, ErrorService):
        return Error_Service().handle_501(error_data=error_data, request=request, context_data=context_data,
                                          app_info=app_info)
    return json_resp(error_no=501, message=error_data.message, sub_message=error_data.sub_message)
