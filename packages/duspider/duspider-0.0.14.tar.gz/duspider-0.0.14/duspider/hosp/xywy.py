# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/1/29 14:32
# https://z.xywy.com/yiyuandiqu-henan.htm
import json

from pydantic import BaseModel
from typing import Union

from duspider.base import Spider
from parsel import Selector


class HospitalHit(BaseModel):
    pr: str
    city: str
    hosp_name: str
    level: Union[None, str] = None  # 医院级别
    area: Union[None, str] = None  # 地区
    medical: Union[None, str] = None  # 医院性质
    medical_insurance: Union[None, str] = None  # 医保

    def __json(self, val):
        if isinstance(val, (list, dict)):
            return json.dumps(val, ensure_ascii=False)
        return val

    def to_db(self) -> dict:
        return {k: self.__json(v) for k, v in self.dict().items()}


class XywySpider(Spider):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://z.xywy.com/yiyuandiqu-henan.htm'
        self.zx_city = ["北京", "上海", "重庆", "天津"]

    async def all(self) -> HospitalHit:
        res = await self.get(self.start_url)
        doc = Selector(res.text)
        pr_list = doc.css('div.sidebar ul.clearfix > li')
        for pr_span in pr_list:
            href = pr_span.xpath('./a/@href').get('').strip()
            pr = pr_span.xpath('./a//span[1]/text()').get('').strip()
            if '.xywy.com' in href:
                if not href.startswith('http'):
                    href = f'https:{href}'
                res = await self.get(href)
                async for row in self.city(pr, res):
                    yield row

    async def city(self, pr, res):
        doc = Selector(res.text)
        div_list = doc.css('div.pr.f14 > div')
        for div in div_list:
            city = div.xpath('./div[1]/text()').get('').strip()

            li_list = div.xpath('./div[2]//li')
            for li in li_list:
                name = li.xpath('./a/text()').get('').strip()
                text = li.xpath('./span/text()').get('').strip().replace('(', '').replace(')', '')
                text = text.split(' ')
                level, medical, medical_insurance = None, None, None
                if len(text) == 1:
                    level = text[0]
                elif len(text) == 2:
                    level, medical = text
                elif len(text) == 3:
                    level, medical, medical_insurance = text

                yield HospitalHit(
                    pr='直辖市' if pr in self.zx_city else pr,
                    city=pr if pr in self.zx_city else city,
                    hosp_name=name,
                    level=level,
                    medical=medical,
                    area=city if pr in self.zx_city else None,
                    medical_insurance=medical_insurance,
                )


if __name__ == '__main__':
    import asyncio

    s = XywySpider()
    asyncio.run(s.all())
