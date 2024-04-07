# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/3/7 14:51
# 罕见病数据
# see https://www.orpha.net/en/disease
from du_aio_tools.base_spider import BaseSpider


class Orpha(BaseSpider):
    def __init__(self):
        super().__init__()

    def parse_category_xml(self):
        """解析类别数据XML"""

    def parse_alignments_xml(self):
        """解析对齐方式 XML"""
