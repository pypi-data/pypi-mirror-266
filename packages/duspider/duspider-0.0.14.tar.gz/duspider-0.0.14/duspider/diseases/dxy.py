# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/12/1 9:32
# see https://dxy.com/diseases
import json
import logging
import re
import time

import requests

from duspider.exceptions import RequestError
from loguru import logger
from parsel import Selector
from pydantic import BaseModel

from duspider.base import Spider
from duspider.tools import get_ua

logger = logging.getLogger("duspider.diseases.dxy")


class DxyHit(BaseModel):
    url: str
    name: str
    html: str


class DDxy(Spider):
    """丁香园-疾病"""

    def __init__(self):
        super().__init__()
        self.start_url = 'https://dxy.com/diseases'
        self.detail_url = ''

    def get_headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            # 'Connection': 'keep-alive',
            # 'Cookie': 'csrfToken=e3K0D6gTCgrTaduM8bqOP59F; dxy_da_cookie-id=463fd7ae00b024f795c8b23da4cbf8cf1701394331199; Hm_lvt_f21c182642df0697ca3ebaf7a82b8fc4=1701394333; _ga=GA1.2.812475353.1701394344; _gid=GA1.2.1681936883.1701394344; _gat=1; Hm_lpvt_f21c182642df0697ca3ebaf7a82b8fc4=1701413462; _ga_SQH0F3ZX3P=GS1.2.1701411160.3.1.1701413462.0.0.0',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': 'https://dxy.com/diseases',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': get_ua(),
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    async def category(self, html):

        js_data = re.findall('<script>window\.\$\$data=(.*?)</script>', html, flags=re.I | re.M)
        if js_data:
            js_data = js_data[0]
            data = json.loads(js_data)
            async for row in self.parse_list(data, href=''):
                yield row

            for i in data['sections'][1:]:
                href = i['href']
                res = await self.get(href)
                if res.status_code == 200:
                    js_data = re.findall('<script>window\.\$\$data=(.*?)</script>', res.text, flags=re.I | re.M)
                    if js_data:
                        js_data = js_data[0]
                        data = json.loads(js_data)

                        async for row in self.parse_list(data, href):
                            yield row
                else:
                    logger.error(f'请求异常：[{res}] - [{href}]')

        else:
            logger.error(f'json解析异常：[{len(js_data)}]')

    async def get(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                headers = self.get_headers()
                resp = requests.get(url,
                                    headers=headers,
                                    timeout=self.timeout,
                                    **kwargs)
                if '访问过于频繁，请' in resp.text:
                    logger.warning('访问过于频繁, 暂停100s')
                    time.sleep(100)
                    raise RequestError(url, err=err, retry=i)
                return resp
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''

    async def parse_list(self, data, href):
        # if not data.get('diseases'):
        #     print(href, data)
        for row in data['diseases']:
            for i in row['tag_list']:
                view = i.get('view')
                if view:
                    i = view
                    url = f'https://dxy.com/disease/{i["id"]}/detail'
                    res = await self.get(url)
                    if res.status_code == 200:
                        yield await self.parse_info(res.text, url)

                    else:
                        logger.error(f'请求异常：[{res}] - [{url}]')

    async def parse_info(self, html, url='') -> DxyHit:
        js_data = re.findall('<script>window\.\$\$data=(.*?)</script>', html, flags=re.I | re.M)[0]
        data = json.loads(js_data)
        try:
            name = data['disease']['title']
            return DxyHit(html=js_data, url=url, name=name)
        except Exception as e:
            logger.error(e)
            return None

    async def all(self):
        res = await self.get(self.start_url)
        if res.status_code == 200:
            async for row in self.category(res.text):
                yield row
        else:
            logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def pages(self, url):
        """翻页"""
        res = await self.get(url)
        if res.status_code == 200:
            doc = Selector(res.text)
            async for row in self.parse_list(doc):
                yield row

            # 翻页
            max_num = doc.css('ul.result_item_dots > li > span:nth-last-child(4)::text')
            if max_num:
                max_num = int(max_num)
                for page in range(2, max_num):
                    href = url + f'_p{page}'
                    res = await self.get(href)
                    if res.status_code == 200:
                        doc = Selector(res.text)
                        async for row in self.parse_list(doc):
                            yield row
        else:
            logger.error(f'请求异常：[{res}] - [{url}]')

    async def run(self):
        async for row in self.all():
            print(row.name)
            print(row.url)
            print(row.html)
            input('!')


if __name__ == '__main__':
    jbk = DDxy()
    import asyncio

    asyncio.run(jbk.run())
