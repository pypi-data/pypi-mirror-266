# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/29 11:42
# see https://www.dayi.org.cn/about
import logging
import re
import json
from math import ceil
from loguru import logger

from parsel import Selector
from pydantic import BaseModel, validator

from duspider.base import Spider
from duspider.tools import make_md5, get_ua

logger = logging.getLogger("duspider.diseases.dayiorg")


class DaYiOrgHit(BaseModel):
    uid: str
    url: str
    html: str
    name: str


class DaYiOrg(Spider):
    """中国医药信息查询平台-疾病"""

    def __init__(self, page_size=30):
        super().__init__()
        self.page_size = page_size
        self.start_url = 'https://api2.dayi.org.cn/api/disease/list2'
        self.detail_url = 'https://www.dayi.org.cn/disease/{}.html'

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent': get_ua()
        }

    async def all(self):
        params = {
            'tabType': 1,
            'navType': 2,
        }
        res = await self.get(self.start_url, params=params, headers=self.headers)
        if res.status_code == 200:
            data = res.json()
            total = data['totalCount']
            data_list = data['list']
            async for row in self.parse_list(data_list):
                yield row
            nums = ceil(total / 30)
            logger.debug(f'nums: [{nums}]')

            # 迭代其他分类的列表数据
            for i in range(2, nums + 1):
                params = {
                    'pageNo': i,
                    'pageSize': 30,
                }
                resp = await self.get(self.start_url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    data_list = data['list']
                    async for row in self.parse_list(data_list):
                        yield row
                else:
                    logger.error(f'请求异常：[{resp}] - [{resp.text}]')

        else:
            logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def parse_list(self, data):
        for row in data:
            url = self.detail_url.format(row['id'])
            res = await self.get(url, headers=self.headers)
            if res.status_code == 200:
                uid = make_md5(url)
                yield DaYiOrgHit(uid=uid, name=row["title"], url=url, html=res.text)
            else:
                logger.error(f'请求异常：[{url}] - [{res}] - [{res.text}]')

    async def run(self):
        # await self.all()
        async for row in self.all():
            print(row.uid)
            print(row.url)
            print(row.name)
            input('!')


if __name__ == '__main__':
    bd = DaYiOrg()
    import asyncio

    asyncio.run(bd.run())
