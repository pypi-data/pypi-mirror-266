# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/1/9 14:51
# see http://fund.keyanzhiku.com/Index
import logging
import re

from tqdm import tqdm
from parsel import Selector

from duspider.base import Spider
from duspider.fund.nsfc import NSFCHit

from duspider.tools import get_ua

logger = logging.getLogger(__file__)


class KYZS(Spider):

    def __init__(self, cookies):
        """
        :param cookies: 登录状态后的cookies
        """
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': get_ua(),
        }
        super().__init__()
        self.cookies = cookies
        self.url = 'http://fund.keyanzhiku.com/Index/index/start_year/0/end_year/0/xmid/0/search/1/p/{}.html'

        self.info_url = 'https://kd.nsfc.gov.cn/api/baseQuery/conclusionProjectInfo/'
        self.size = 5
        self.sta = False

    async def get_pages(self):
        url = self.url.format('1')
        html = await self.get(url, headers=self.headers, cookies=self.cookies)
        pages = int(re.findall('\d+ 条数据 \d+/(\d+) 页', html.text)[0])
        return html, pages

    @staticmethod
    def parse_text(text):
        return text.split('：', 1)[-1].strip()

    async def parse(self, name, url, html) -> NSFCHit:

        doc = Selector(html)
        inner_doc = doc.css('div.layui-table-box')
        ratify_no = self.parse_text(inner_doc.xpath('//div[contains(text(), "批准号")]/text()').get(''))
        data = NSFCHit(url=url,
                       uid=ratify_no,
                       ratify_no=ratify_no,
                       project_name=name)

        data.approval_year = int(self.parse_text(inner_doc.xpath('//div[contains(text(), "批准年度")]/text()').get('')))
        data.project_apply_code = self.parse_text(inner_doc.xpath('//div[contains(text(), "学科分类")]/text()').get(''))
        data.project_leader = self.parse_text(inner_doc.xpath('//div[contains(text(), "项目负责人")]/text()').get(''))
        data.project_category = self.parse_text(inner_doc.xpath('//div[contains(text(), "项目类别")]/text()').get(''))
        data.project_unit = self.parse_text(inner_doc.xpath('//div[contains(text(), "依托单位")]/text()').get(''))
        project_funding = self.parse_text(inner_doc.xpath('//div[contains(text(), "资助金额")]/text()').get(''))
        data.project_funding = project_funding.split('万')[0]
        year_str = self.parse_text(inner_doc.xpath('//div[contains(text(), "研究期限")]/text()').get(''))
        year_list = re.findall('(\\d)', year_str)
        max_year = max([int(i) for i in year_list])

        # data.report_year = data.approval_year + max_year  # 结题年份
        data.report_year = None
        data.info = '{}'
        data.start_date = f'{data.approval_year}-01-01'  # 开始年份
        data.end_date = f'{data.approval_year + max_year}-12-31'  # 结束年份

        data.project_keyword_c = self.parse_text(
            inner_doc.xpath('//div[contains(text(), "中文主题词")]/text()').get(''))
        data.project_keyword_e = self.parse_text(
            inner_doc.xpath('//div[contains(text(), "英文主题词")]/text()').get(''))

        return data

    async def parse_list(self, url, html):
        """解析列表页数据"""
        doc = Selector(html)
        data_list = doc.css('div.layui-card-body > ul > a')
        for row in data_list:
            http = 'http://fund.keyanzhiku.com/'
            href = row.xpath('./@href').get('').strip()
            if not href.startswith(http):
                href = f'http://fund.keyanzhiku.com{href}'
            name = row.xpath('.//h3/text()').get('').strip()
            headers = self.headers
            headers['Referer'] = url
            resp = await self.get(href, headers=headers, cookies=self.cookies)
            yield await self.parse(name, href, resp.text)

    async def all(self):
        html, pages = await self.get_pages()
        for page in tqdm(range(2, pages + 1)):
            url = self.url.format(str(page))
            resp = await self.get(url, headers=self.headers, cookies=self.cookies)
            async for row in self.parse_list(url, resp.text):
                yield row

    async def run(self):
        async for row in self.all():
            print(row)
            input()


if __name__ == '__main__':
    cookies = {
        'PHPSESSID': 'na1gbukv07qpc4me5sio8b0el4',
        '__51cke__': '',
        'fund_uid': '399822',
        'userinfo': 'think%3A%7B%22openid%22%3A%22oWAAR6Ip3zVBWKFXg9Lno3wSe3HM%22%2C%22name%22%3A%22%25E6%259D%258E%25E5%25A8%259C%22%2C%22img%22%3A%22https%253A%252F%252Fthirdwx.qlogo.cn%252Fmmopen%252Fvi_32%252FFY8Eib47TdmvjlRCUYC6NUogzjU6ia3cdc7iaibWdu52PwPoD7M1ia6G15yarlSg9h9FssHy0yfKnUibfXWHnyFG1Bug%252F132%22%2C%22sex%22%3A%220%22%2C%22sha_cookie%22%3A%2235aaee4401afa1f02da2cd245f85dfba%22%2C%22uid%22%3A%22399822%22%2C%22sid%22%3A%22%22%2C%22url%22%3A%22aHR0cDovL2Z1bmQua2V5YW56aGlrdS5jb20vaW5kZXgucGhwP3M9L0luZGV4L3Bjd3hsb2dpbi9zaWQvYm1FeFoySjFhM1l3TjNGd1l6UnRaVFZ6YVc4NFlqQmxiRFE9Lmh0bWw%253D%22%7D',
        'openid': 'oWAAR6Ip3zVBWKFXg9Lno3wSe3HM',
        'udata': 'e7e233254cdcdd267cf0590b18332758',
        '__tins__21084525': '%7B%22sid%22%3A%201708498813620%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201708500613620%7D',
        '__51laig__': '9',
    }
    kyzs_obj = KYZS(cookies=cookies)
    import asyncio

    asyncio.run(kyzs_obj.run())
