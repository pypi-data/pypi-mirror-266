from typing import Optional, Any, Callable
from starlette.requests import Request
from pydantic import BaseModel, field_validator


class AppInfo(BaseModel):
    # 编码，如：'afeng_book'
    code: str
    # 标题，如：阿锋书屋
    title: str
    # 数据库编码(默认是：code+‘_db’)，如：'afeng_book_db'
    db_code: Optional[str] = None
    # 数据库url，如：postgresql://root:123456@127.0.0.1:5432/afeng-book-db
    db_url: Optional[str] = None
    # 路径前缀，如：'/book'
    prefix: Optional[str] = None
    # 是否全是json接口
    is_json_api: Optional[bool] = None
    # 副标题
    sub_title: Optional[str] = None
    # 介绍
    description: Optional[str] = None
    # 关键字
    keywords: Optional[list[str]] = None
    # 域信息，如：https://www.afenghome.com
    origin: Optional[str] = None
    # 网站logo图地址，如：/static/image/logo/logo.png
    logo_image: Optional[str] = '/static/image/logo.png'
    # 网站favicon.ico
    favicon_ico: Optional[str] = '/favicon.ico'
    # 备案信息，如：'京ICP备2023032898号-1'
    icp_record_info: Optional[str] = None
    # 公安备案信息，如：京公网安备11000002000001号
    police_record_info: Optional[str] = None
    # 公安备案号：11000002000001
    police_record_code: Optional[str] = None
    # 联系信息，如：'QQ: 1640125562'
    contact_info: Optional[str] = None
    # 联系QQ，如：'1640125562'
    contact_qq: Optional[str] = None
    # 联系邮箱，如：'afengbook@aliyun.com'
    contact_email: Optional[str] = None
    # 问题反馈链接
    feedback_url: Optional[str] = None
    # app根路径：os.path.dirname(__file__)
    root_path: Optional[str] = None
    # app的web路径：os.path.join(root_path, 'web')
    web_path: Optional[str] = None
    # 错误处理服务, 类继承自：ErrorService
    error_service_class: Optional[str] = 'afeng_tools.fastapi_tool.common.service.error_base_service.DefaultErrorService'
    # 500异常后后台工作函数，如发送邮件, async def send_email(request: Request, exception: Exception, traceback_msg: str)
    error500_background_work_func: Optional[Callable[[Request, Exception, str], None]] = None
    # 额外的数据参数
    data_dict: Optional[dict[str, Any]] = None

    @field_validator('db_code')
    @classmethod
    def set_db_code(cls, v: Any):
        if not v:
            return cls.code + '_db'
        return v


class BaiduInfo(BaseModel):
    app_id: str
    app_key: str
    app_secret_key: str
    sign_key: Optional[str] = None


class WeixinInfo(BaseModel):
    app_id: str
    app_secret_key: str
    token: Optional[str] = None
    encoding_aes_key: Optional[str] = None
    token_file: Optional[str] = None
    msg_callback: Optional[Callable[[Any], None]] = None


class EmailInfo(BaseModel):
    # 昵称
    nickname: str
    # 登录邮箱
    login_email: str
    # 密码
    password: Optional[str] = None
