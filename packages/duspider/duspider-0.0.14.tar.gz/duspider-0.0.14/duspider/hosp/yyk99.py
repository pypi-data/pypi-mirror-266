# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/2/22 10:05
# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/1/29 14:32
from tqdm import tqdm

from duspider.base import Spider
from parsel import Selector

from duspider.hosp.xywy import HospitalHit


class YYK99(Spider):
    """99医院库"""

    def __init__(self):
        super().__init__()
        self.start_url = 'https://yyk.99.com.cn/city.html'
        self.exclude = ["香港", "澳门", "台湾"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}

    async def all(self) -> HospitalHit:
        res = await self.get(self.start_url, headers=self.headers)
        doc = Selector(res.text)
        dl_list = doc.css('li.on div.m-clump > dl')
        for dl in dl_list:
            pr = dl.xpath('./dt/a/text()').get('').strip()  # 区域
            dd_list = dl.xpath('./dd/a')  # 区域的医院列表
            # print('省/直辖市:', pr)
            for dd in tqdm(dd_list):
                city = dd.xpath('string(.)').get('').strip()
                href = dd.xpath('./@href').get('').strip()
                if not href.startswith('http'):
                    href = f'https://yyk.99.com.cn{href}'
                if pr not in self.exclude:
                    resp = await self.get(href, headers=self.headers)
                    async for row in self.city(pr, city, resp.text):
                        yield row

    async def city(self, pr, city, res):
        doc = Selector(res)
        td_list = doc.css('div.m-table-2 td')

        for td in td_list:
            name = td.xpath('./a/@title').get('').strip()
            href = td.xpath('./a/@href').get('').strip()
            if not href.startswith('http'):
                href = f'https://yyk.99.com.cn{href}'
            item = HospitalHit(
                pr=pr,
                city=city,
                hosp_name=name,
            )
            resp = await self.get(href, headers=self.headers)
            yield self.parse(item, resp.text)

    def parse(self, item, res):
        doc = Selector(text=res)
        item.level = doc.css('div.wrap_title > span:nth-child(2)::text').get('').strip()
        item.medical = doc.css('div.wrap_title > span:nth-child(3)::text').get('').strip()
        return item

    async def run(self):
        async for row in self.all():
            print(row)
            input('aa')


if __name__ == '__main__':
    import asyncio

    hdf = YYK99()
    asyncio.run(hdf.run())
