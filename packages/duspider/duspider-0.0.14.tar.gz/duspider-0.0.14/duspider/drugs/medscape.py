# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/9 8:46
# see https://reference.medscape.com/drugs
import logging
import re
import time
import json
from typing import List, Any, Dict

from math import ceil
from parsel import Selector
from pydantic import BaseModel

from duspider.base import HEADERS, Spider
from duspider.exceptions import LocationTypeError
from duspider.tools import make_md5

logger = logging.getLogger("duspider.drugs.medscape")


class MedScapeHit(BaseModel):
    uid: str  # 药品 id
    brand_name: str  # 通用名、商品名
    groups: str  # 类别 Classes
    dosage_forms_and_strengths: str  # 剂型和规格
    dosing_uses: str  # 用法用量 Dosing & Uses
    drug_interaction: List = []  # 药物相互作用
    adverse_effects: str  # 不良反应 Adverse Effects
    contraindications: str  # 禁忌 Contraindications
    cautions: str  # 注意事项 Cautions
    pregnancy_lactation: str  # 注意事项 孕妇及哺乳期妇女用药 Pregnancy & Lactation
    mechanism_action: str  # 作用机制 Mechanism of Action
    absorption: str  # 药代动力学Absorption/Distribution/Metabolism/Elimination
    images: str  # 图片信息 Images
    overdose: str  # 药物过量 OVERDOSE
    missed_dose: str  # 错过服药时间 MISSED DOSE
    storage: str  # 贮存 STORAGE

    # 通用名、商品名和别名Brand and Other Names、

    def __json(self, val):
        if isinstance(val, (list, dict)):
            return json.dumps(val, ensure_ascii=False)
        return val

    def json(self) -> dict:
        return {k: self.__json(v) for k, v in self.dict().items()}


class MedScape(Spider):

    def __init__(self, max_retry=3, sem=15, **kwargs):
        super().__init__(max_retry=max_retry, sem=sem, **kwargs)
        self.start_url = 'https://reference.medscape.com/drugs'
        self.search_url = 'https://search.medscape.com/search/'

    async def all(self):
        """全库数据采集"""
        resp = await self.get(self.start_url)
        doc = Selector(resp.text)
        a_list = doc.css('ul.classdruglist > li > a')
        for a in a_list:
            href = a.xpath('./@href').get('').strip()
            await self.parse_drug_list(href)

    async def parse_drug_list(self, url):
        """药物列表"""
        resp = await self.get(url)
        doc = Selector(resp.text)
        a_list = doc.css("div.topic-section  li > a")
        for a in a_list:
            href = a.xpath('./@href').get('').strip()
            data, html = await self.get_data(url=href, html=True)
            yield data, html

    async def query(self, name, html):
        """名称检索"""
        params = {'q': name, 'plr': 'ref', 'page': '1'}
        resp = await self.get(self.search_url, params=params)
        if resp:
            doc = Selector(resp.text)
            # profreference > div > p.searchResultTitle
            title_list = doc.css('#profreference > div')
            for div in title_list:
                ti = div.css('p.searchResultTitle::text').get('')
                print("ti:", ti)
                if ti.lower().strip() == name.lower.strip():
                    href = div.css('p.searchResultTitle > a::attr(href)').get('').strip()
                    if not href.startswith('http'):
                        href = f'https:{href}'
                    return await self.get_data(url=href, html=html)
        raise TypeError('未检索到结果')

    async def get_data(self, url=None, name=None, html=False):
        """查询"""
        if url:
            resp = await self.get(url)
            if resp:
                data = await self.parse_html(resp.text, url)
                if html:
                    return data, resp.text
                return html
        elif name:
            return await self.query(name, html)
        raise TypeError('输入无效')

    async def parse_html(self, html, url):
        """药物数据页面"""
        doc = Selector(html)
        uid = make_md5(url)
        print(url)


if __name__ == '__main__':
    med = MedScape()
    import asyncio

    # res = asyncio.run(drug.get_data('DB09532'))
    # res = asyncio.run(drug.get_data('DB00091'))
    res = asyncio.run(med.get_data(name='Cyclosporine'))
    print(res)
