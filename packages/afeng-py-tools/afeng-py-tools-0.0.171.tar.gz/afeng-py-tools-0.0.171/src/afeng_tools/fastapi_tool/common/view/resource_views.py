import os.path
import time
from typing import Optional

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.baidu_pan_tool import baidu_pan_tools
from afeng_tools.fastapi_tool import fastapi_router_tools, fastapi_response_tools
from afeng_tools.fastapi_tool.common.enum import ResourceFormatEnum
from afeng_tools.fastapi_tool.common.service.resource_base_service import ResourceService
from afeng_tools.fastapi_tool.fastapi_response_tools import resp_file
from afeng_tools.fastapi_tool.template.item import Error404DataItem
from afeng_tools.log_tool.loguru_tools import get_logger
from fastapi import BackgroundTasks, APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

logger = get_logger()


class ResourceView:
    """
    使用示例：router = ResourceView(app_info.db_code, ResourceInfoPo).router
    """
    def __init__(self, db_code: str, po_model_type: type):
        self.db_code = db_code
        self.po_model_type = po_model_type
        self._router = fastapi_router_tools.create_router(prefix='/resource', tags=['资源'])
        self.resource_service = ResourceService(self.db_code, self.po_model_type)
        self._router.get('/public/{resource_code}', response_class=RedirectResponse)(self.get_public_resource)
        self._router.get('/access/{resource_code}')(self.get_access_resource)
        self._router.get('/download/{resource_code}')(self.get_download_resource)

    @property
    def router(self):
        return self._router

    @classmethod
    def resp_not_found(self, request: Request):
        return fastapi_response_tools.resp_404(error_data=Error404DataItem(
            message='很抱歉，找不到资源！', sub_message='您访问的资源不存在或已被删除！ (｡•ˇ‸ˇ•｡)'),
                                               request=request)

    async def get_public_resource(self, request: Request, background_tasks: BackgroundTasks,
                                  resource_code: Optional[str] = None):
        if resource_code is None or resource_code == 'None' or not resource_code:
            return self.resp_not_found(request=request)
        if os.path.exists(os.path.join(settings_tools.get_config(SettingsKeyEnum.server_static_save_path), 'resource',
                                       resource_code)):
            return RedirectResponse(f'/static/resource/{resource_code}')
        resource_info_po = self.resource_service.get_by_code(resource_code)
        if resource_info_po is None:
            return self.resp_not_found(request=request)
        if resource_info_po.expire_timestamp and int(time.time()) >= resource_info_po.expire_timestamp:
            if resource_info_po.resource_format == ResourceFormatEnum.image:
                resource_info_po = self.resource_service.refresh_baidu_img_access_url(resource_info_po)
            else:
                return self.resp_not_found(request=request)
        if resource_info_po.access_url:
            background_tasks.add_task(self.resource_service.run_local_cache, resource_code, resource_info_po.access_url)
            return resource_info_po.access_url
        elif resource_info_po.resource_format == ResourceFormatEnum.image and resource_info_po.baidu_fs_id:
            resource_info_po = self.resource_service.refresh_baidu_img_access_url(resource_info_po)
            if resource_info_po.access_url:
                background_tasks.add_task(self.resource_service.run_local_cache, resource_code,
                                          resource_info_po.access_url)
                return resource_info_po.access_url
        if resource_info_po.local_path:
            return f'/resource/access/{resource_code}'
        return self.resp_not_found(request=request)

    async def get_access_resource(self, request: Request, resource_code: str):
        resource_info_po = self.resource_service.get_by_code(resource_code)
        if resource_info_po is None:
            return self.resp_not_found(request=request)
        if resource_info_po.local_path and os.path.exists(resource_info_po.local_path):
            return resp_file(resource_info_po.local_path, resource_info_po.resource_name,
                             resource_info_po.download_flag)
        else:
            return self.resp_not_found(request=request)

    async def get_download_resource(self, request: Request, resource_code: str):
        resource_info_po = self.resource_service.get_by_code(resource_code)
        if resource_info_po is None:
            return self.resp_not_found(request=request)
        if resource_info_po.local_path and os.path.exists(resource_info_po.local_path):
            return resp_file(resource_info_po.local_path, resource_info_po.resource_name,
                             resource_info_po.download_flag)
        if resource_info_po.baidu_fs_id:
            download_url = baidu_pan_tools.get_baidu_download_url(resource_info_po)
            if download_url:
                if download_url.startswith('http://'):
                    download_url = 'https://' + download_url.removeprefix('http://')
                return RedirectResponse(download_url, headers={
                    'Host': 'd.pcs.baidu.com',
                    'User-Agent': 'pan.baidu.com'
                })
        return self.resp_not_found(request=request)
