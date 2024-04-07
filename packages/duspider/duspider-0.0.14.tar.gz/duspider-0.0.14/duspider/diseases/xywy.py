# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/12/4 9:52
# see http://jib.xywy.com/html/a.html
# 寻医问药
import logging

from pydantic import BaseModel

from parsel import Selector

from duspider.base import Spider

logger = logging.getLogger("duspider.diseases.xywy")


class XYWYHit(BaseModel):
    url: str
    html: str
    name: str


class XYWY(Spider):
    """寻医问药-疾病"""

    def __init__(self):
        super().__init__(max_retry=10)
        self.start_url = 'http://jib.xywy.com/html/{}.html'
        self.detail_url = ''
        self.domain = 'http://jib.xywy.com'  # 域名
        self.overview = '/il_sii/gaishu/'  # 概述
        self.encoding = 'GB2312'

    async def all(self):
        """遍历字母"""
        for i in range(97, 123):
            url = self.start_url.format(chr(i))
            res = await self.get(url, headers=self.get_headers())
            if res.status_code == 200:
                res.encoding = self.encoding
                async for row in self.d_list(res.text):
                    yield row
            else:
                logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def d_list(self, html):
        """科室"""
        doc = Selector(html)
        div_list = doc.css('ul.ks-zm-list > li')

        for div in div_list:
            href = div.css('a::attr(href)').get('').strip()

            if not href.startswith('http'):
                href = href.split('il_sii_')[-1]
                href = self.overview + href
                href = f'{self.domain}{href}'

            resp = await self.get(href, headers=self.get_headers())
            if resp.status_code == 200:
                resp.encoding = self.encoding
                yield await self.parse_info(resp.text, href)
            else:
                logger.error(f'请求异常：[{resp}] - [{href}]')

    async def parse_info(self, html, url) -> XYWYHit:
        """不同数据据存在不同的页面中， 需要单独请求"""
        doc = Selector(html)
        all_html = doc.css('div.jib-articl').get('').strip()
        name = doc.css('div.jb-name::text').get('').strip()
        li_list = doc.css('div.jib-nav li')[1:]
        for li in li_list:
            href = li.xpath('./a/@href').get('').strip()
            if not href.startswith('http'):
                href = f'{self.domain}{href}'
            resp = await self.get(href, headers=self.get_headers())
            if resp.status_code == 200:
                resp.encoding = self.encoding
                _doc = Selector(resp.text)
                _temp_html = _doc.css('div.jib-articl').get('').strip()
                all_html += _temp_html
        return XYWYHit(url=url, html=all_html, name=name)

    async def run(self):
        async for row in self.all():
            if row:
                print(row.name)
                print(row.url)
                print(row.html)
                input('!')


if __name__ == '__main__':
    X = XYWY()
    import asyncio

    asyncio.run(X.run())
