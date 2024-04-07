# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/2/22 10:05
# 医学百科
# http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8

from duspider.base import Spider
from parsel import Selector

from duspider.hosp.xywy import HospitalHit


class AHospital(Spider):
    """ 医学百科网站 """

    def __init__(self):
        super().__init__()
        self.start_url = 'http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'
        self.info_url = f'http://www.a-hospital.com/w/%s'  # 详情链接
        self.exclude = ["香港", "澳门", "台湾"]
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
        span_list = doc.css('#bodyContent > *')
        start = False
        for span in span_list:
            text = span.get().strip()
            if text.startswith('<h3>'):
                pr = span.xpath('.//text()').get('').strip()
                if not start:
                    start = True
            if start:
                if text.startswith('<p>'):
                    a_list = span.xpath('./a')
                    for i in a_list:
                        # print(i.get())
                        if i.attrib.get('rel'):
                            #  跳过未撰写的城市
                            continue

                        city = i.xpath('./text()').get('').strip()
                        href = i.xpath('./@href').get('').strip()
                        if pr not in self.exclude:
                            if not href.startswith('http'):
                                href = f'http://www.a-hospital.com{href}'
                            resp = await self.get(href)
                            async for row in self.city(pr, city, resp.text):
                                yield row

    async def city(self, provinces, city, res):
        """市"""
        doc = Selector(text=res)
        li_list = doc.xpath('//h2/span[contains(text(),"医院列表")]/../following::ul[1]/li')
        for li in li_list:  # 遍历城市
            name = li.xpath('./b/a/text()').get('').strip()
            href = li.xpath('./b/a/@href').get('')
            if not href.startswith('http'):
                href = f'http://www.a-hospital.com{href}'

            item = HospitalHit(
                pr=provinces,
                city=city,
                hosp_name=name,
            )
            resp = await self.get(href, headers=self.headers)
            yield self.parse(item, resp.text)

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
        item.level = doc.xpath('//b[text()="医院等级"]/../a/text()').get('').strip()
        item.medical = doc.xpath('//b[text()="医院类型"]/../a/text()').get('').strip()
        return item

    async def run(self):
        async for row in self.all():
            print(row)
            input('aa')


if __name__ == '__main__':
    import asyncio

    hdf = AHospital()
    asyncio.run(hdf.run())
