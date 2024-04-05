from starlette.requests import Request
from starlette.responses import RedirectResponse
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.fastapi_tool.fastapi_response_tools import resp_template
from afeng_tools.fastapi_tool.template.service import template_render_service

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.fastapi_tool.template.item import TemplateHtmlHeadData, TemplateShowQrcodeAreaData, \
    TemplateRedirectAreaData, AppinfoDataItem
from afeng_tools.http_tool import http_request_tools, http_params_tools
from afeng_tools.pydantic_tool.model.common_models import LinkItem


def create_html_head_data(_app_info: AppInfo, is_mobile: bool, title: str, description: str = None,
                          keyword_list: list[str] = None,
                          author: str = None, favicon: str = None, origin: str = None, ) -> TemplateHtmlHeadData:
    if title is not None:
        title = f'{title}|{_app_info.title}|{_app_info.sub_title}'
    if description is None:
        description = f'{title}:{_app_info.description}'
    if keyword_list is None:
        keyword_list = [title]
        keyword_list.extend(_app_info.keywords)
    else:
        keyword_list = [tmp for tmp in keyword_list if tmp is not None]
    if author is None:
        author = 'chentiefeng'
    if favicon is None:
        favicon = '/favicon.ico'
    if origin is None:
        origin = _app_info.origin
    return TemplateHtmlHeadData(is_mobile=is_mobile, title=title, description=description,
                                keyword_list=keyword_list,
                                author=author, favicon=favicon, origin=origin)


def redirect_to(request: Request, target: str,
                app_info_item: AppinfoDataItem = AppinfoDataItem(title='阿锋之家'),
                page_title: str = '跳转中心',
                page_favicon_ico: str = '/static/image/favicon.ico',
                back_url: str = '/',
                ad_list: list[LinkItem] = None,
                template_file: str = 'common/views/redirect/index.html',
                group_code: str = 'common/redirect'):
    if not target:
        return RedirectResponse('/')
    if target.startswith('%2F'):
        target = http_params_tools.url_decode(target)
    is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
    context_data = {
        'is_mobile': is_mobile,
        'title': page_title,
        'favicon_ico': page_favicon_ico
    }
    download_area_template_name, download_area_template_file = template_render_service.get_template_redirect_area(
        group_code=group_code,
        context_data_func=lambda: TemplateRedirectAreaData(
            is_mobile=is_mobile,
            app_info=app_info_item,
            ad_list=ad_list,
            redirect_url=target,
            back_url=back_url
        ),
        reload_freq=ReloadFreqEnum.always)
    context_data['template_redirect_area'] = download_area_template_file
    return resp_template(request, template_file=template_file, context_data=context_data)


def redirect_to_qrcode_page(request: Request,
                            qrcode_image_url: str = '/static/image/qrcode/wx_of_qrcode.jpg',
                            qrcode_image_title: str = '公众号：阿锋之家',
                            message_list: list[str] = None,
                            page_title: str = '请关注公众号：阿锋之家',
                            page_favicon_ico: str = '/static/image/favicon.ico',
                            template_file: str = 'common/views/alert/index.html',
                            group_code: str = 'common/show_qrcode'):
    is_mobile = http_request_tools.is_mobile(request.headers.get('user-agent'))
    context_data = {
        'is_mobile': is_mobile,
        'title': page_title,
        'favicon_ico': page_favicon_ico
    }
    if message_list is None:
        message_list = [
            '1、打开微信',
            '2、扫描上方二维码',
            '3、关注"阿锋之家"',
        ]
    download_area_template_name, download_area_template_file = template_render_service.get_template_show_qrcode_area(
        group_code=group_code,
        context_data_func=lambda: TemplateShowQrcodeAreaData(
            is_mobile=is_mobile,
            qrcode_image_url=qrcode_image_url,
            qrcode_image_title=qrcode_image_title,
            message_list=message_list
        ),
        reload_freq=ReloadFreqEnum.always)
    context_data['template_alert_area'] = download_area_template_file
    return resp_template(request, template_file=template_file, context_data=context_data)
