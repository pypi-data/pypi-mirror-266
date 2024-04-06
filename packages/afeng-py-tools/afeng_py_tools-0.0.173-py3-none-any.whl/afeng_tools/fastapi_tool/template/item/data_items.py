"""
数据项
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class PageDataItem(BaseModel):
    """分页数据项"""
    # 当前页
    current_page: Optional[int] = 1
    # 分页大小
    page_size: Optional[int] = 10
    # 总数量
    total_count: Optional[int] = 0
    # 总页数
    total_page: Optional[int] = 0
    # 数据列表
    data_list: Optional[list[Any]] = None


class CalendarDataItem(BaseModel):
    """日历项"""
    date: Optional[str] = Field(title='日期', default=None)
    value: Optional[Any] = Field(title='数据', default=None)
    href: Optional[str] = Field(title='链接地址', default=None)


class AppinfoDataItem(BaseModel):
    # 应用标题
    title: Optional[str] = None
    # logo图片
    logo_image: Optional[str] = '/static/image/logo/logo.png'
    # 应用链接
    url: Optional[str] = '/'


class Error404DataItem(BaseModel):
    """错误404数据"""
    # 页面标题
    title: Optional[str] = '404-Not Found'
    # 错误信息
    message: Optional[str] = '很抱歉，找不到网页！'
    # 子消息
    sub_message: Optional[str] = '您访问的页面不存在或已被删除！ (｡•ˇ‸ˇ•｡)'


class Error500DataItem(BaseModel):
    """错误500数据"""
    # 页面标题
    title: Optional[str] = '500-服务器错误'
    # 错误信息
    message: Optional[str] = '服务器内部错误（Internal Server Error）'
    # 子消息
    sub_message: Optional[str] = '当您看到这个页面，表示服务器内部错误，此网站可能遇到技术问题，无法执行您的请求，请稍后重试或联系管理员进行处理，感谢您的支持！'
    # 等待秒数
    wait_seconds: Optional[int] = 30
    # 管理员联系方式， 如：mailto:afengbook@aliyun.com
    contact_info_url: Optional[str] = None


class Error501DataItem(BaseModel):
    """错误501数据"""
    # 页面标题
    title: Optional[str] = '501-操作失败'
    # 错误信息，如：很抱歉，无法完成您的操作
    message: Optional[str] = '操作失败'
    # 子消息， 如：很抱歉，无法完成您的操作，请进行<a href="https://txc.qq.com/products/622359" target="_blank">问题反馈</a>，感谢您的支持！
    sub_message: Optional[str] = '如果要解决该问题，请进行问题反馈，感谢您的支持！'
    # 管理员联系方式， 如：mailto:afengbook@aliyun.com
    contact_info_url: Optional[str] = None
    # 问题反馈链接, 如：https://txc.qq.com/products/622359
    feedback_url: Optional[str] = None
