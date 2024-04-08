from sqlalchemy import BigInteger, Column, Text, String, Enum, Boolean, DateTime, func, Float
from afeng_tools.fastapi_tool.common.enum import IconTypeEnum, ResourceFormatEnum, SitemapFreqEnum
from afeng_tools.sqlalchemy_tools.core import sqlalchemy_base_model


class CommonPo:
    """
    通用模型: 使用示例：
        common_po = CommonPo(db_code=app_info.db_code)
        GroupInfoPo, CategoryInfoPo, ResourceInfoPo, LinkInfoPo, TagInfoPo, BlacklistInfoPo, SitemapInfoPo, ArticleInfoPo = common_po.GroupInfoPo, common_po.CategoryInfoPo, common_po.ResourceInfoPo, common_po.LinkInfoPo, common_po.TagInfoPo,common_po.BlacklistInfoPo, common_po.SitemapInfoPo, common_po.ArticleInfoPo
    """

    def __init__(self, db_code: str):
        self.db_code = db_code
        self.BaseModel = sqlalchemy_base_model.get_base_model(db_code=db_code)
        self.GroupInfoPo = self._create_group_po()
        self.CategoryInfoPo = self._create_category_po()
        self.ResourceInfoPo = self._create_resource_po()
        self.LinkInfoPo = self._create_link_po()
        self.TagInfoPo = self._create_tag_po()
        self.BlacklistInfoPo = self._create_blacklist_po()
        self.SitemapInfoPo = self._create_sitemap_po()
        self.ArticleInfoPo = self._create_article_po()

    def _create_group_po(self) -> type:
        class GroupInfoPo(self.BaseModel):
            """分组信息"""
            __tablename__ = "tb_group_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src  = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型',
                               unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)

        return GroupInfoPo

    def _create_category_po(self) -> type:
        class CategoryInfoPo(self.BaseModel):
            """分类信息"""
            __tablename__ = "tb_category_info"
            group_code = Column(String(100), comment='分组编码', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型',
                               unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)
            parent_code = Column(String(100), comment='父编码', unique=False, nullable=True)

        return CategoryInfoPo

    def _create_resource_po(self) -> type:
        class ResourceInfoPo(self.BaseModel):
            """资源信息"""
            __tablename__ = "tb_resource_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            resource_code = Column(String(100), comment='资源编码', index=True, unique=True, nullable=True)
            resource_name = Column(String(255), comment='资源名称', unique=False, nullable=True)
            resource_format = Column(Enum(ResourceFormatEnum), comment='资源格式（image:图片）', unique=False,
                                     nullable=True)
            local_path = Column(String(500), comment='本地路径', unique=False, nullable=True)
            baidu_fs_id = Column(BigInteger, comment='百度fs_id', unique=False, nullable=True)
            access_url = Column(String(500), comment='访问url', unique=False, nullable=True)
            expire_timestamp = Column(BigInteger, comment='过期时间戳', unique=False, nullable=True)
            download_flag = Column(Boolean, comment='下载标志', default=False)

        return ResourceInfoPo

    def _create_link_po(self) -> type:
        class LinkInfoPo(self.BaseModel):
            """链接信息"""
            __tablename__ = "tb_link_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(100), comment='标题', unique=False, nullable=True)
            description = Column(Text, comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型',
                               unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)
            link_url = Column(String(500), comment='链接地址', unique=False, nullable=True)

        return LinkInfoPo

    def _create_tag_po(self) -> type:
        class TagInfoPo(self.BaseModel):
            """标签信息"""
            __tablename__ = "tb_tag_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=True, nullable=True, index=True)
            title = Column(String(100), comment='标题', unique=False, nullable=True)
            description = Column(String(255), comment='描述', unique=False, nullable=True)

        return TagInfoPo

    def _create_blacklist_po(self) -> type:
        class BlacklistInfoPo(self.BaseModel):
            """黑名单信息"""
            __tablename__ = "tb_blacklist_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            type_value = Column(String(255), comment='类型值', unique=False, nullable=True)

        return BlacklistInfoPo

    def _create_sitemap_po(self) -> type:
        class SitemapInfoPo(self.BaseModel):
            """站点地图信息"""
            __tablename__ = "tb_sitemap_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            loc_url = Column(String(500), comment='url地址', unique=False, nullable=True)
            # 0.0 ~ 1.0
            priority = Column(Float, comment='优先权', unique=False, nullable=True)
            last_mod = Column(String(100), comment='最新一次更新时间(YYYY-MM-DD或，YYYY-MM-DDThh:mm:ss)', unique=False,
                              nullable=True)
            change_freq = Column(Enum(SitemapFreqEnum), comment='更新频率',
                                 default=SitemapFreqEnum.daily, unique=False, nullable=True)
            parent_id = Column(BigInteger, comment='主键', unique=False, nullable=True)

        return SitemapInfoPo

    def _create_article_po(self) -> type:
        class ArticleInfoPo(self.BaseModel):
            """帮助信息"""
            __tablename__ = "tb_article_info"
            type_code = Column(String(100), comment='类型编码', default='default', unique=False, nullable=True)
            code = Column(String(100), comment='编码', unique=False, nullable=True, index=True)
            title = Column(String(255), comment='标题', unique=False, nullable=True)
            sub_title = Column(String(255), comment='副标题', unique=False, nullable=True)
            description = Column(String(255), comment='描述', unique=False, nullable=True)
            image_src = Column(Text, comment='图标源地址', unique=False, nullable=True)
            icon_type = Column(Enum(IconTypeEnum, values_callable=lambda x: [i.value.value for i in x]),
                               comment='图标类型',
                               unique=False, nullable=True)
            icon_value = Column(Text, comment='图标值', unique=False, nullable=True)
            source_info = Column(String(255), comment='来源信息', unique=False, nullable=True)
            author_info = Column(String(255), comment='作者信息', unique=False, nullable=True)
            publish_time = Column(DateTime, comment='发布时间', default=func.now())
            content = Column(Text, comment='内容', unique=False, nullable=True)

        return ArticleInfoPo
