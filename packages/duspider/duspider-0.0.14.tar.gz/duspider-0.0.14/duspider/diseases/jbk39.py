# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/29 16:24
# see https://jbk.39.net/bw/t1/
import logging
import re
import time

import requests
from pydantic import BaseModel

from duspider.exceptions import RequestError
from parsel import Selector

from duspider.base import Spider
from duspider.tools import get_ua

logger = logging.getLogger("duspider.diseases.jbk39")


class JBKHit(BaseModel):
    url: str
    html: str
    name: str


class JBK39(Spider):
    """39健康网-疾病"""

    def __init__(self):
        super().__init__(max_retry=10)
        self.start_url = 'https://jbk.39.net/bw/toubu_t1/'
        self.detail_url = ''

    def get_headers(self):
        return {
            'authority': 'jbk.39.net',
            'user-agent': get_ua()
        }

    async def all(self):
        res = await self.get(self.start_url, headers=self.get_headers())
        if res.status_code == 200:
            async for row in self.dept(res.text):
                yield row
        else:
            logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def dept(self, html):
        """科室"""
        doc = Selector(html)
        d_list = doc.css('div.lookup_position > div.menu_box_c > ul > li')
        for d in d_list[1:]:
            href = d.xpath('.//a/@href').get('').strip()

            if not href.startswith('http'):
                href = f'https://jbk.39.net{href}'
            if '_t1' not in href:
                href = f'{href.rstrip("/")}_t1/'
            res = await self.get(href, headers=self.get_headers())
            if res.status_code == 200:
                async for row in self.category(res.text, href):
                    yield row
            else:
                logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def pages(self, url):
        """翻页"""
        res = await self.get(url, headers=self.get_headers())
        if res.status_code == 200:
            doc = Selector(res.text)
            async for row in self.parse_list(doc):
                yield row
            # 翻页
            page = re.findall('if \(page_num >= 1 && page_num <= (\d+) \) ', res.text, flags=re.S | re.M)
            if page:
                max_num = int(page[0])
                logger.debug(f'max_num: [{max_num}]-[{url}]')
                for page in range(2, max_num + 1):
                    href = url.rstrip('/') + f'_p{page}'
                    res = await self.get(href, headers=self.get_headers())

                    if res.status_code == 200:
                        doc = Selector(res.text)
                        async for row in self.parse_list(doc):
                            yield row
        else:
            logger.error(f'请求异常：[{res}] - [{url}]')

    async def parse_list(self, doc):
        div_list = doc.css('div.result_content > div')
        for div in div_list:
            href = div.css('a::attr(href)').get('').strip()
            resp = await self.get(href, headers=self.get_headers())
            if resp.status_code == 200:
                yield await self.parse_info(resp.text, href)
            else:
                logger.error(f'请求异常：[{resp}] - [{href}]')

    async def get_info(self):
        """详情"""

    async def parse_info(self, html, url) -> JBKHit:
        """不同数据据存在不同的页面中， 需要单独请求"""
        doc = Selector(html)
        all_html = ''
        name = doc.css('div.disease > h1::text').get('').strip()
        ul_list = doc.css('div.left_navigation > div.navigation')[1:-1]
        for ul in ul_list:
            li_list = ul.xpath('.//li')
            for li in li_list:
                href = li.xpath('./a/@href').get('').strip()
                resp = await self.get(href, headers=self.get_headers())
                if resp.status_code == 200:
                    _doc = Selector(resp.text)
                    _temp_html = _doc.css('div.list_left').get('').strip()
                    all_html += _temp_html

        return JBKHit(url=url, html=all_html, name=name)

    async def category(self, html, href):
        """类别"""
        doc = Selector(html)
        ul_list = doc.css('ul.type_subscreen_unit li')
        if ul_list:
            async for row in self.sub_category(ul_list):
                yield row
        else:
            async for row in self.pages(href):
                yield row

    async def sub_category(self, ul_list):
        """二级类别"""
        for li in ul_list:
            href = li.css('a::attr(href)').get('').strip()
            if not href.startswith('http'):
                href = f'https://jbk.39.net{href}'
            if '_t1' not in href:
                href = f'{href.rstrip("/")}_t1/'

            name = li.xpath('.//a/text()').get('').strip()
            # https://jbk.39.net/bw/bi_t1_p2/
            async for row in self.pages(href):
                yield row

    async def run(self):
        async for row in self.all():
            print(row)
            if row:
                print(row.name)
                print(row.url)
                # print(row.html)
                # input('!')


if __name__ == '__main__':
    jbk = JBK39()
    import asyncio

    asyncio.run(jbk.run())
