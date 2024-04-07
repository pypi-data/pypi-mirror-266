# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/1/29 14:32
# https://z.xywy.com/yiyuandiqu-henan.htm
import json
import re

from pydantic import BaseModel
from typing import Union

from duspider.base import Spider
from parsel import Selector

from duspider.hosp.xywy import HospitalHit
from duspider.tools import get_ua

class HaoDF(Spider):
    """ 好大夫网站 """

    def __init__(self):
        super().__init__()
        self.start_url = 'https://www.haodf.com/yiyuan/beijing/list.htm'
        self.provinces_list = []
        self.headers = {
            "Content-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
        }

    async def all(self):
        """所有数据"""
        resp = await self.get(self.start_url)
        async for row in self.provinces(resp.text):
            yield row

    async def provinces(self, res):
        """省"""
        doc = Selector(text=res)
        provinces_list = doc.css('#el_tree_1000000 > div')
        for provinces in provinces_list:  # 遍历省/直辖市
            provinces_name = provinces.css('a ::text').get('')
            provinces_url = provinces.css('a ::attr(href)').get('')
            if provinces_name and provinces_name != '朝阳':
                provinces = provinces_name
                url = f'https:{provinces_url}'
                resp = await self.get(url)
                async for row in self.city(provinces, resp.text):  # 获取市列表
                    yield row

    async def city(self, provinces, res):
        """市"""
        doc = Selector(text=res)
        city_list = doc.css('#el_tree_1000000 > div.ksbd > ul > li')
        for city_ in city_list:  # 遍历城市
            city = city_.css('a ::text').get('')
            city_ul = city_.css('a ::attr(href)').get('')
            city_ul = f'https:{city_ul}'
            resp = await self.get(city_ul)
            async for row in self.hospital_list(provinces, city, resp.text):  # 获取区域列表
                yield row

    async def hospital_list(self, provinces, city, res):
        doc = Selector(text=res)
        hospital_list = doc.css('.m_ctt_green >ul >li')
        for hospital_ in hospital_list:  # 遍历医院列表
            hospital = hospital_.css('a ::text').get('').strip('')
            href = hospital_.css('a ::attr(href)').get('').strip('')
            # hospital_tag = hospital_.css('span ::text').get('').replace(' ', '')
            if not href.startswith('http'):
                href = f'https://www.haodf.com{href}'
            item = HospitalHit(pr=provinces,
                               city=city,
                               hosp_name=hospital)
            resp = await self.get(href)
            yield self.parse(item, resp.text)

    def parse(self, item: HospitalHit, res):
        doc = Selector(res)
        item.level = doc.css('div.info-lable > span:nth-child(2)::text').get('').strip()
        item.medical = doc.css('div.info-lable > span:nth-child(3)::text').get('').strip()
        return item

    async def run(self):
        async for row in self.all():
            print(row)
            input('aa')


if __name__ == '__main__':
    import asyncio

    hdf = HaoDF()
    asyncio.run(hdf.run())
