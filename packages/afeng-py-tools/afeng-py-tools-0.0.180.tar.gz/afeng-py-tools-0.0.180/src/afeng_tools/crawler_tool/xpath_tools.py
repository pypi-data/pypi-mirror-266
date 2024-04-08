"""
xpath工具： 安装：pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
html_tree.xpath('//div')
    . 本级，表示当前节点
    ..  上一级
    // 任意节点
    /  直接子节点
    *  任意元素  如： //*  选取文档中的所有元素
    //div[@class="A"]//text()  选择分区A中的所有文本
    //div[@class="A"]//text()[normalize-space()]  过滤掉空白字符串
    [@*]  获取带有属性的标签
    [@属性名]  获取带有某个属性的标签
    [@属性名="属性值"]  获取带有某个属性值的标签
    [contains(@属性名,"属性值")]  获取带有某个属性包含某个属性值的标签， 如：//a[contains(text(),"闻")]  或  //a[contains(@class,'active')]  class样式包含active
    [contains(.,"测试")]  标签包含某个值
    [starts‐with(@属性名,"开头值")]  开头匹配, 如： //a[starts-with(text(),"新")]
    [substring(@属性名,1)="data"]  获取带有某个属性的值的结尾子字符串是data的标签
    [@属性名1="属性值1" and @属性名2="属性值2"]  获取带有属性值1和属性值2的标签
    [name(.)!="a"]  排除某个标签
    a[last()]  获取a标签最后一个元素
    [position()> 1] 和 [position()< last()]  忽略xpath中的第一个和最后一个元素
    [text()="文本值"]  文本值等于某个值
    [text()=" 楼" and text()="栋" and text()="数： "]   多标签分隔字符串查找
    [text()[normalize-space()]  去除字符串空格换行
    //div[@class="tr-line clearfix"]/div/div[contains(text(),"层")]/text()  模糊查找标签内容字符保护层的元素
    /following-sibling::div  获取弟节点div
    /preceding-sibling::div  获取兄节点div
    /parent::div  获取父节点div
    [not(@class or @id)] 不包含某个属性
    [not(@class)] 不包含, 如： //tbody/tr[not(@class)]  排除有class属性标签
    [not(contains(@class, "disabled"))]  排除某个class属性标签

    //table/tr[not(@class=“tbhead”) and @class=“head"]  匹配所有的tr中不包含 tbhead 属性 和包含 head 的tr标签
    string(//p)  返回标签内包含字符串
    xpath("//tr[6]/td[2]/text() | //tr[7]/td[2]/text()")  在一个xpath中写的多个表达式用 `|` 分开， 每个表达式互不干扰
"""

from lxml import etree
from lxml.etree import _Element as Element, _ElementUnicodeResult as ElementUnicodeResult


def get_html_tree(html_file: str) -> Element:
    """转换html文件为html_tree"""
    parser = etree.HTMLParser(encoding="utf-8")
    return etree.parse(html_file, parser=parser)


def parse_to_html_tree(html_text: str) -> Element:
    """转换字符串为html_tree"""
    return etree.HTML(html_text)


def get_first(html_tree, xpath: str) -> Element | ElementUnicodeResult:
    """获取第一个元素"""
    result_list = html_tree.xpath(xpath)
    if result_list:
        return result_list[0]


def get_list(html_tree, xpath: str) -> list[Element] | list[ElementUnicodeResult]:
    """获取元素列表"""
    return html_tree.xpath(xpath)


def to_string(element: Element, only_text: bool = False,
              pretty_print: bool = False, encoding: str = 'utf8',
              with_comments: bool = True) -> str | None:
    """
    元素转为字符串
    :param element: xpath元素
    :param only_text: 是否只打印文本内容，默认是打印html代码
    :param pretty_print: 是否漂亮的打印
    :param encoding: 编码
    :param with_comments: 是否附带注释
    :return:
    """
    if not element:
        return
    if only_text:
        return element.text
    return etree.tostring(element, pretty_print=pretty_print, encoding=encoding, method='html',
                          with_comments=with_comments).decode()
