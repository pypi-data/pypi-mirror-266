from enum import Enum
from typing import Optional, Callable

from afeng_tools.datetime_tool.datetime_tools import one_minute_seconds, one_hour_seconds, one_day_seconds, \
    one_week_seconds
from afeng_tools.pydantic_tool.model.common_models import EnumItem


class IconTypeEnum(Enum):
    """图标类型枚举"""
    font_icon = EnumItem(title='文字图标')
    base64_icon = EnumItem(title='Base64图标')
    svg_icon = EnumItem(title='svg图标')
    image_icon = EnumItem(title='图片图标')
    resource_icon = EnumItem(title='资源图标')


class ReloadFreqItem(EnumItem):
    """更新频率项"""
    # 秒值
    seconds_value: int
    # 判断函数：返回True则进行Reload， 如：def func (timestamp) -> bool
    judge_func: Optional[Callable[[float], bool]] = None


class ReloadFreqEnum(Enum):
    """更新频率枚举"""
    always = ReloadFreqItem(title='一直更新', seconds_value=0, judge_func=lambda x: True)
    half_hourly = ReloadFreqItem(title='半小时更新一次', seconds_value=30 * one_minute_seconds)
    hourly = ReloadFreqItem(title='每小时更新一次', seconds_value=one_hour_seconds)
    eight_hourly = ReloadFreqItem(title='8小时更新一次', seconds_value=8 * one_hour_seconds)
    daily = ReloadFreqItem(title='每天更新一次', seconds_value=one_day_seconds)
    weekly = ReloadFreqItem(title='每周更新一次', seconds_value=one_week_seconds)
    monthly = ReloadFreqItem(title='每月更新一次', seconds_value=30 * one_day_seconds)
    three_monthly = ReloadFreqItem(title='三个月更新一次', seconds_value=90 * one_day_seconds)
    half_yearly = ReloadFreqItem(title='半年更新一次', seconds_value=180 * one_day_seconds)
    yearly = ReloadFreqItem(title='每年更新一次', seconds_value=360 * one_day_seconds)
    never = ReloadFreqItem(title='从不更新', seconds_value=100 * 360 * one_day_seconds, judge_func=lambda x: False)


class SitemapFreqEnum(Enum):
    """站点更新频率"""
    always = 'always'
    hourly = 'hourly'
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'
    yearly = 'yearly'
    never = 'never'


class ResourceFormatEnum(Enum):
    """资源格式枚举"""
    image = 'image'
    file = 'file'


class ResourceUrlEnum(Enum):
    """资源格式枚举"""
    # 资源根路径
    base_url = '/resource/public'
    # 资源下载路径
    download_url = '/resource/download'
