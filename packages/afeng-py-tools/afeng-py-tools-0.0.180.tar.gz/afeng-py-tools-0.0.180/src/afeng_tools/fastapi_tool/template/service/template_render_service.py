"""
模块渲染服务
"""
import os
from datetime import datetime
from typing import Callable

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.fastapi_tool.common.enum import ReloadFreqEnum
from afeng_tools.http_tool.http_url_tool import join_local_url
from afeng_tools.jinja2_tool import jinja2_tools
from afeng_tools.template_tool.template_decorator_tools import html_template

from afeng_tools.fastapi_tool.template.item import TemplateHtmlHeadData, TemplateBreadCrumbData, \
    TemplatePaginationAreaData, TemplateLeftNavData, \
    TemplatePageFooterData, TemplatePageHeaderData, TemplateTopBarData, TemplateLogoSearchData, TemplateFixNavData, \
    TemplatePageSearchHeaderData, TemplateResultListData, TemplateIndexPageHeaderData, TemplateTagListData, \
    TemplateGroupListData, TemplateFilterTypeAreaData, TemplateDayCalendarData, TemplateTabPanelData, \
    TemplateTopRankingData, TemplateRedirectDownloadAreaData, TemplateRedirectAreaData, TemplateError404AreaData, \
    TemplateError500AreaData, TemplateError501AreaData, TemplateShowQrcodeAreaData

template_directory = settings_tools.get_config(SettingsKeyEnum.server_template_path)
template_env = jinja2_tools.create_template_env(directory_list=[template_directory])


def render(do_render_func: Callable, **kwargs) -> tuple[str, str]:
    """渲染"""
    return do_render_func(**kwargs)


def _is_need_reload(save_template_file: str, reload_freq: ReloadFreqEnum = ReloadFreqEnum.weekly) -> bool:
    if not os.path.exists(save_template_file) or reload_freq.always:
        return True
    old_update_time = os.stat(save_template_file).st_mtime
    reload_freq_item = reload_freq.value
    if reload_freq_item.judge_func and isinstance(reload_freq_item.judge_func, Callable):
        return reload_freq_item.judge_func(old_update_time)
    else:
        return (datetime.now().timestamp() - reload_freq_item.seconds_value) > old_update_time


def _render_template_file(app_code: str, template_file: str, group_code: str,
                          context_data_func: Callable,
                          reload_freq: ReloadFreqEnum = ReloadFreqEnum.weekly,
                          **kwargs):
    """渲染模板文件"""

    template_html_file = join_local_url([app_code, template_file])
    tmp_save_html_file = join_local_url(['tmp', app_code, group_code, template_file])
    save_template_file = str(os.path.join(template_directory, tmp_save_html_file.removeprefix('/')))
    if _is_need_reload(save_template_file, reload_freq):
        if kwargs:
            context_data = context_data_func(**kwargs)
        else:
            context_data = context_data_func()
        template_content = jinja2_tools.format_template(template_html_file, context=context_data, env=template_env)
        os.makedirs(os.path.dirname(save_template_file), exist_ok=True)
        with open(save_template_file, 'w', encoding='utf-8') as f:
            f.write('{% raw %}' + template_content + '{% endraw %}')
    return tmp_save_html_file


@html_template(name='template_head', file='views/head/page_head.html')
def get_template_head(group_code: str, context_data_func: Callable[[], TemplateHtmlHeadData],
                      app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                      template_name: str = None, template_file: str = None) -> tuple[str, str]:
    def context_data_func_wrapper():
        data = context_data_func()
        return {
            'is_mobile': data.is_mobile,
            'head_title': data.title,
            'head_description': data.description,
            'head_keywords': ','.join([tmp for tmp in data.keyword_list if tmp]),
            'head_author': data.author,
            'head_favicon': data.favicon,
            'head_origin': data.origin
        }

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_more_head', file='views/head/page_more_head.html')
def get_template_more_head(group_code: str, context_data_func: Callable[[], TemplateHtmlHeadData],
                           app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                           template_name: str = None, template_file: str = None) -> tuple[str, str]:
    return get_template_head(group_code=group_code, context_data_func=context_data_func,
                             app_code=app_code, reload_freq=reload_freq,
                             template_name=template_name, template_file=template_file)


@html_template(name='template_top_bar', file='module_html/header/top_bar.html')
def get_template_top_bar(group_code: str, context_data_func: Callable[[], TemplateTopBarData],
                         app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                         template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面顶部topbar模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_logo_search', file='module_html/header/logo_search.html')
def get_template_logo_search(group_code: str, context_data_func: Callable[[], TemplateLogoSearchData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面顶部logo_search模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_fix_nav', file='module_html/header/fix_nav.html')
def get_template_fix_nav(group_code: str, context_data_func: Callable[[], TemplateFixNavData],
                         app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                         template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面顶部logo_search模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_page_header', file='module_html/page_header.html')
def get_template_page_header(group_code: str, context_data_func: Callable[[], TemplatePageHeaderData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面顶部模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        child_template_tuple_list = [
            get_template_top_bar(group_code=group_code,
                                 context_data_func=lambda: data.topbar_data,
                                 app_code=app_code, reload_freq=reload_freq),
            get_template_logo_search(group_code=group_code,
                                     context_data_func=lambda: data.logo_search_data,
                                     app_code=app_code, reload_freq=reload_freq),
            get_template_fix_nav(group_code=group_code,
                                 context_data_func=lambda: data.fix_nav_data,
                                 app_code=app_code, reload_freq=reload_freq)

        ]
        context_data = {
            'is_mobile': data.is_mobile,
        }
        for child_template_name, child_template_file in child_template_tuple_list:
            context_data[child_template_name] = child_template_file
        return context_data

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_index_page_header', file='module_html/page_index_header.html')
def get_template_index_page_header(group_code: str, context_data_func: Callable[[], TemplateIndexPageHeaderData],
                                   app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                   template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    首页页面顶部模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_page_search_header', file='module_html/page_search_header.html')
def get_template_page_search_header(group_code: str, context_data_func: Callable[[], TemplatePageSearchHeaderData],
                                    app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                    template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面搜索顶部模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_bread_crumb', file='module_html/page/bread_crumb.html')
def get_template_bread_crumb(group_code: str, context_data_func: Callable[[], TemplateBreadCrumbData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    面包屑模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return {
            'page_title': data.page_title,
            'data_list': data.bread_crumb_list,
        }

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_left_nav', file='module_html/page/left_nav.html')
def get_template_left_nav(group_code: str, context_data_func: Callable[[], TemplateLeftNavData],
                          app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                          template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    左侧导航模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_page_footer', file='module_html/page_footer.html')
def get_template_page_footer(group_code: str, context_data_func: Callable[[], TemplatePageFooterData],
                             app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面底部模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_result_list', file='module_html/list/result_list.html')
def get_template_result_list(app_code: str, group_code: str, context_data_func: Callable[[], TemplateResultListData],
                             reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                             template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    页面底部模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_pagination_area', file='module_html/list/pagination_area.html')
def get_template_pagination_area(group_code: str, context_data_func: Callable[[], TemplatePaginationAreaData],
                                 app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                 template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """结果模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        if data.pre_btn and data.pre_btn.title is None:
            data.pre_btn.title = '上一页'
        if data.next_btn and data.next_btn.title is None:
            data.next_btn.title = '下一页'
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_tag_list', file='module_html/list/tag_list.html')
def get_template_tag_list(group_code: str, context_data_func: Callable[[], TemplateTagListData],
                          app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                          template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    标签列表模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_group_list', file='module_html/list/group_list.html')
def get_template_group_list(group_code: str, context_data_func: Callable[[], TemplateGroupListData],
                            app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                            template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """
    分组列表模板
    :param group_code: 分组编码
    :param context_data_func: 上下文数据生成函数
    :param app_code:
    :param reload_freq:
    :param template_name:
    :param template_file:
    :return:
    """

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_filter_type_area', file='module_html/list/filter_type_area.html')
def get_template_filter_type_area(group_code: str, context_data_func: Callable[[], TemplateFilterTypeAreaData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """过滤类型模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_day_calendar', file='module_html/list/day_calendar.html')
def get_template_day_calendar(group_code: str, context_data_func: Callable[[], TemplateDayCalendarData],
                              app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                              template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """结果模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_tab_panel', file='module_html/page/tab_panel.html')
def get_template_tab_panel(group_code: str, context_data_func: Callable[[], TemplateTabPanelData],
                           app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                           template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """Tab面板模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_top_ranking_list', file='module_html/ranking_list/top_ranking_list.html')
def get_template_top_ranking_list(group_code: str, context_data_func: Callable[[], TemplateTopRankingData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """热点数据排行模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_redirect_download_area', file='module_html/redirect/download_area.html')
def get_template_redirect_download_area(group_code: str,
                                        context_data_func: Callable[[], TemplateRedirectDownloadAreaData],
                                        app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                        template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """下载区域模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_redirect_area', file='module_html/redirect/redirect_area.html')
def get_template_redirect_area(group_code: str,
                               context_data_func: Callable[[], TemplateRedirectAreaData],
                               app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                               template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """下载区域模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_show_qrcode_area', file='module_html/alert/show_qrcode_area.html')
def get_template_show_qrcode_area(group_code: str,
                                  context_data_func: Callable[[], TemplateShowQrcodeAreaData],
                                  app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                  template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """显示二维码模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_error_404_area', file='module_html/error/404_area.html')
def get_template_error_404_area(group_code: str,
                                context_data_func: Callable[[], TemplateError404AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """404错误区域模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_error_500_area', file='module_html/error/500_area.html')
def get_template_error_500_area(group_code: str,
                                context_data_func: Callable[[], TemplateError500AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """500错误区域模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)


@html_template(name='template_error_501_area', file='module_html/error/501_area.html')
def get_template_error_501_area(group_code: str,
                                context_data_func: Callable[[], TemplateError501AreaData],
                                app_code: str = 'common', reload_freq: ReloadFreqEnum = ReloadFreqEnum.always,
                                template_name: str = None, template_file: str = None) -> tuple[str, str]:
    """500错误区域模板"""

    def context_data_func_wrapper():
        data = context_data_func()
        return data.model_dump()

    return template_name, _render_template_file(app_code, template_file,
                                                group_code=group_code, context_data_func=context_data_func_wrapper,
                                                reload_freq=reload_freq)
