# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/16 15:38
# see https://drugs.medlive.cn/drugref/drugCate.do?treeCode=H010101
import logging
import re
import time
from abc import ABC, abstractmethod

import requests
from parsel import Selector

from duspider.base import HEADERS, Spider
from duspider.exceptions import LocationTypeError, RequestError
from duspider.tools import make_md5

logger = logging.getLogger("duspider.drugs.medlive")


class MedLive(Spider, ABC):

    def __init__(self, headers, cookies, max_retry=3, sem=15, **kwargs):
        super().__init__(max_retry=max_retry, sem=sem, **kwargs)
        self.headers = headers
        self.cookies = cookies
        self.sess = requests.Session()
        self.start_url = 'https://drugs.medlive.cn/drugref/drugCateIndex.do'

    @abstractmethod
    async def ocr_capt(self):
        """验证码识别"""

    async def auto_login(self, user, pwd):
        """登录"""

    async def get(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = self.sess.get(url,
                                     timeout=self.timeout,
                                     **kwargs)

                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''

    def cookies_to_dict(self, cookies):
        new_cookies = {}
        for i, k in cookies.items():
            new_cookies[i] = k
        return new_cookies

    async def all(self):
        """全库数据采集"""
        resp = await self.get(self.start_url, headers=self.headers, cookies=self.cookies)
        # print(resp.headers)
        set_cookies = self.cookies_to_dict(resp.cookies)
        if resp.status_code == 200:
            doc = Selector(resp.text)
            a_list = doc.css('div.three-table > div.table1 a')
            for i in a_list:
                href = i.xpath('./@href').get('').strip()
                # https://drugs.medlive.cn/drugref/drugCate2nd.do?treeCode=H01
                if href:
                    href = f"https://drugs.medlive.cn/{href}"
                    async for row in self.category(href, set_cookies):
                        yield row

    async def run(self):
        async for row in self.all():
            print(row)
            print(row.text)
            input('ss')

    async def pages(self, url):
        headers = self.headers.copy()
        # headers['Referer'] = 'https://drugs.medlive.cn/drugref/drugCateIndex.do'
        headers['Referer'] = url
        resp = await self.get(url, cookies=self.cookies, headers=headers)
        if resp.status_code == 200:
            async for row in self.parse_list(resp):
                yield row
            doc = Selector(resp.text)
            span = doc.css('body > div.search-content > div.fenye > ul > span::text').get('').strip()
            pages = re.findall('共(\\d+)页', span)
            if pages:
                pages = int(pages[0])
            if pages > 1:
                for page in range(2, pages + 1):
                    p_url = url + f'&page={page}'
                    res = await self.get(p_url, headers=headers, cookies=self.cookies)
                    async for row in self.parse_list(res):
                        yield row

    async def parse_list(self, res):
        doc = Selector(res.text)
        # a_list = doc.css('div.three-table > div.table1 a')
        a_list = doc.css('div.box-list > div a')
        for i in a_list:
            url = i.xpath('./@href').get('')
            if url and not url.startswith('http'):
                url = f'https://drugs.medlive.cn/{url}'
            yield await self.get(url, headers=self.headers, cookies=self.cookies)

    async def category(self, url, set_cookies):
        headers = self.headers.copy()
        cookies = self.cookies.copy()
        cookies.update(set_cookies)
        headers['Referer'] = 'https://drugs.medlive.cn/drugref/drugCateIndex.do'
        headers['Referer'] = url
        resp = await self.get(url,
                              cookies=cookies,
                              headers=headers
                              )
        print('history', resp.history)
        if resp.status_code == 200:
            doc = Selector(resp.text)
            a_list = doc.css('div.table-class a')  # todo 无数据
            for a in a_list:
                href = a.xpath('./@href').get('').strip()
                # https://drugs.medlive.cn/drugref/drugCate2nd.do?treeCode=H01
                if href:
                    href = f"https://drugs.medlive.cn/{href}"
                    async for row in self.pages(href):
                        yield row

    async def category_sub(self, url):
        resp = await self.get(url, cookies=self.cookies, headers=self.headers)
        if resp.status_code == 200:
            doc = Selector(resp.text)
            a_list = doc.css('div.table-class a')  # todo 无数据
            for a in a_list:
                href = a.xpath('./@href').get('').strip()
                # https://drugs.medlive.cn/drugref/drugCate2nd.do?treeCode=H01
                if href:
                    href = f"https://drugs.medlive.cn/{href}"
                    async for row in self.pages(href):
                        yield row

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
    cookies = {
        'Hm_lvt_62d92d99f7c1e7a31a11759de376479f': '1700558681',
        'JSESSIONID': '3C91CE28B0431968B042FEB198AF0BD4',
        'ymtinfo': 'eyJ1aWQiOiI1MzIxMzQ3IiwicmVzb3VyY2UiOiIiLCJleHRfdmVyc2lvbiI6IjEiLCJhcHBfbmFtZSI6IiJ9',
        'Hm_lpvt_62d92d99f7c1e7a31a11759de376479f': '1700619726',
        'ymt_pk_id': '1c47467b1bb9d241',
        '_pk_ref.3.a971': '%5B%22%22%2C%22%22%2C1700619726%2C%22https%3A%2F%2Fwww.medlive.cn%2F%22%5D',
        '_pk_id.3.a971': '1c47467b1bb9d241.1700558683.2.1700619726.1700558683.',
        '_pk_ses.3.a971': '*',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': 'https://www.medlive.cn/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    med = MedLive(cookies=cookies, headers=headers)
    import asyncio

    # res = asyncio.run(drug.get_data('DB00091'))
    res = asyncio.run(med.run())
    # print(res)
