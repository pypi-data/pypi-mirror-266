# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2023/11/27 16:59
# see https://jiankang.baidu.com/widescreen/entitylist
import json
import logging
import re

from pydantic import BaseModel, validator

from duspider.base import Spider
from duspider.tools import make_md5

logger = logging.getLogger("duspider.diseases.baidu")


class BaiduDisease(BaseModel):
    overview: str  # 概述
    alias: str  # 别名
    disease_definition: str  # 疾病定义
    department: str  # 就诊科室
    epidemiology: str  # 流行病学
    transmission: str  # 传播途径
    disease_type: str  # 疾病类型
    pathogen: str  # 病因
    symptoms: str  # 症状
    treat: str  # 治疗
    prognosis: str  # 预后
    everyday: str  # 日常
    medical_treatment: str  # 就医

    # 就医 （就医 + 诊断流程 + 诊断依据 + 就诊科室 + 相关检查 + 鉴别诊断）


class BaiduHit(BaseModel):
    name: str
    url: str
    uid: str
    html: str

    def parse(self) -> BaiduDisease:
        data = self.get_js_data()
        # return BaiduDisease()

    def get_js_data(self, html=None):
        """解析 html 中的 json 数据"""
        js_data = re.findall('componentData:(.*?)commonData:', html or self.html, flags=re.S)[0].strip().rstrip(
            '"},\n },').strip() + '"}}'
        return js_data


class Baidu(Spider):
    """百度医典"""

    def __init__(self):
        super().__init__()
        self.start_url = 'https://jiankang.baidu.com/widescreen/api/entitylist'

    async def disease(self):
        return

    async def all(self):
        params = {
            'tabType': 1,
            'navType': 2,
        }
        res = await self.get(self.start_url, params=params)
        if res.status_code == 200:
            data = res.json()
            item_list = data['itemList']
            # 迭代其他分类的列表数据
            for item in item_list:
                params['itemType'] = item['name']
                resp = await self.get(self.start_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    # 返回其他分类的列表数据
                    for k, v in data['entityList'].items():
                        async for row in self.entity_list(v):
                            yield row
                else:
                    logger.error(f'请求异常：[{resp}] - [{resp.text}]')
        else:
            logger.error(f'请求异常：[{res}] - [{res.text}]')

    async def entity_list(self, data):
        for row in data:
            name = row['name']
            url = row['url']
            res = await self.get(url)
            if res.status_code == 200:
                uid = make_md5(url)
                yield BaiduHit(uid=uid, name=name, url=url, html=res.text)
            else:
                logger.error(f'请求异常：[{url}] - [{res}] - [{res.text}]')

    async def run(self):
        # await self.all()
        async for row in self.all():
            print(row.uid)
            print(row.url)
            print(row.name)
            print(json.loads(row.get_js_data()))
            input('!')


if __name__ == '__main__':
    bd = Baidu()
    import asyncio

    asyncio.run(bd.run())
