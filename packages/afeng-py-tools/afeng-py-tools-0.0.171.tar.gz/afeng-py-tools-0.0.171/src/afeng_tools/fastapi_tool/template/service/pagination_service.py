from afeng_tools.pydantic_tool.model.common_models import LinkItem


def get_pagination_data(page_num: int, page_size: int, total_page: int, href_prefix: str,
                        up_num: int = 3,
                        page_num_attr: str = 'page_num',
                        page_size_attr: str = 'page_size') -> list[LinkItem]:
    """获取分页值"""
    start_num = page_num - 4
    if start_num <= 0:
        start_num = 1
    end_num = page_num + up_num
    if end_num > total_page:
        end_num = total_page
    result_list = []
    for tmp_num in range(start_num, end_num + 1):
        result_list.append(LinkItem(title=str(tmp_num), is_active=(page_num == tmp_num),
                                    href=f'{href_prefix}&{page_num_attr}={tmp_num}&{page_size_attr}={page_size}'))
    return result_list


def init_page_value(page_num: int, page_size: int, default_page_size: int = 10, max_page_size: int = 50):
    """初始化分页值"""
    if page_num <= 0:
        page_num = 1
    if page_size <= 0 or page_size > max_page_size:
        page_size = default_page_size
    return page_num, page_size


def create_page_btn(page_num: int, page_size: int, total_page: int, href_prefix: str,
                    pre_btn_title: str = '上一页', next_btn_title: str = '下一页',
                    page_num_attr: str = 'page_num',
                    page_size_attr: str = 'page_size') -> tuple[int, LinkItem, LinkItem]:
    """创建分页按钮"""
    if page_num > total_page:
        page_num = total_page
    pre_btn, next_btn = None, None
    if page_num > 1:
        pre_btn = LinkItem(title=pre_btn_title,
                           href=f'{href_prefix}&{page_num_attr}={page_num - 1}&{page_size_attr}={page_size}')
    if page_num < total_page:
        next_btn = LinkItem(title=next_btn_title,
                            href=f'{href_prefix}&{page_num_attr}={page_num + 1}&{page_size_attr}={page_size}')
    return page_num, pre_btn, next_btn
