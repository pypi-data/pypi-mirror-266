import os
import re
from typing import Any

import requests

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.baidu_pan_tool import baidu_pan_tools
from afeng_tools.baidu_pan_tool.tools import baidu_pan_file_meta_tools
from afeng_tools.fastapi_tool.common.enum import ResourceUrlEnum, ResourceFormatEnum
from afeng_tools.fastapi_tool.common.po_service.resource_po_service_ import ResourcePoService
from afeng_tools.fastapi_tool.common.service.base_service import BaseService
from afeng_tools.http_tool import http_download_tools
from afeng_tools.sqlalchemy_tools.crdu import base_crdu


class ResourceService(BaseService):
    """
    使用示例：resource_service = ResourceService(app_info.db_code, ResourceInfoPo, app_code=app_info.code)
    """

    po_service_type = ResourcePoService

    def get_by_code(self, resource_code: str) -> Any:
        """
        通过编码查询
        :param resource_code: 资源编码
        :return: ResourceInfoPo
        """
        return self.po_service.get(self.po_model_type.resource_code == resource_code)

    def query_in_code(self, resource_code_list: list[str]) -> list[Any]:
        """通过编码列出"""
        return self.po_service.query_more(self.po_model_type.resource_code.in_(resource_code_list))

    @classmethod
    def get_resource_url(cls, url: str, resource_code: str) -> str:
        if url:
            return url
        if resource_code:
            return f'{ResourceUrlEnum.base_url.value}/{resource_code}'

    def refresh_baidu_img_access_url(self, resource_info_po) -> Any:
        """刷新百度图片资源的访问路径"""
        if resource_info_po and resource_info_po.resource_format == ResourceFormatEnum.image and resource_info_po.baidu_fs_id:
            baidu_access_token = baidu_pan_tools.get_access_token()
            file_info_list = baidu_pan_file_meta_tools.get_file_metas(baidu_access_token, [resource_info_po.baidu_fs_id], thumb=1)
            if file_info_list:
                access_url = file_info_list[0].thumbs.url3
                resource_info_po.access_url = access_url
                re_search = re.search('&time=(.*?)&', access_url)
                if re_search:
                    resource_info_po.expire_timestamp = int(re_search.group(1)) + 8 * 3600 - 100
                base_crdu.update(resource_info_po, db_code=self.db_code)
                return resource_info_po
        return resource_info_po

    @classmethod
    def get_baidu_download_url(cls, resource_info_po) -> str:
        """获取百度网盘文件下载链接"""
        if resource_info_po and resource_info_po.baidu_fs_id and resource_info_po.resource_format == ResourceFormatEnum.file:
            baidu_access_token = baidu_pan_tools.get_access_token()
            file_info_list = baidu_pan_file_meta_tools.get_file_metas(baidu_access_token, [resource_info_po.baidu_fs_id],
                                                            d_link=1)
            if file_info_list:
                file_info = file_info_list[0]
                # 官方不允许使用浏览器直接下载超过50MB的文件， 超过50MB的文件需用开发者原生的软件或者app进行下载
                # if file_info.size <= 50 * 1024 * 1024:
                down_url = file_info.dlink + f'&access_token={baidu_access_token}'
                down_resp = requests.head(down_url, headers={
                    'Host': 'd.pcs.baidu.com',
                    'User-Agent': 'pan.baidu.com'
                })
                if down_resp.status_code == 302:
                    return down_resp.headers.get('Location')

    @classmethod
    def run_local_cache(cls, resource_code: str, resource_url: str, subfix: str = None, local_cache_path: str = None):
        """运行本地缓存"""
        if local_cache_path is None:
            local_cache_path = os.path.join(settings_tools.get_config(SettingsKeyEnum.server_static_save_path), 'resource')
        os.makedirs(local_cache_path, exist_ok=True)
        if subfix:
            http_download_tools.download_file(resource_url, save_path=local_cache_path,
                                              save_file_name=f'{resource_code}{subfix}')
        else:
            http_download_tools.download_file(resource_url, save_path=local_cache_path, save_file_name=str(resource_code))

    def download_and_add_image_resource(self, image_title: str, image_url: str, group_path: str,
                                        image_name: str = None) -> Any:
        """下载并添加图片资源"""
        pan_path = f'/apps/www/{self.app_code}/image/{group_path}'
        include_filename = False
        if image_name:
            include_filename = True
            pan_path = pan_path + f'/{image_name}'
        result = baidu_pan_tools.save_to_pan(file_url=image_url,
                                             pan_path=pan_path,
                                             include_filename=include_filename)
        if result.errno == 0:
            return self.add_resource(result.fs_id, resource_format=ResourceFormatEnum.image.value,
                                     resource_name=f'[{image_title}]{result.server_filename}')

    def add_resource(self, fs_id: int, resource_format: ResourceFormatEnum, access_url: str = None,
                     download_flag: bool = False,
                     resource_name: str = None) -> Any:
        """添加资源"""
        po = self.po_model_type(
            resource_code=fs_id,
            baidu_fs_id=fs_id,
            resource_format=resource_format,
            download_flag=download_flag,
            resource_name=resource_name,
        )
        if access_url:
            po.access_url = access_url
            re_search = re.search('&time=(.*?)&', access_url)
            if re_search:
                po.expire_timestamp = int(re_search.group(1)) + 8 * 3600 - 100
        return base_crdu.save(po, self.po_model_type.resource_code == po.resource_code, exist_update=False,
                              db_code=self.db_code)
