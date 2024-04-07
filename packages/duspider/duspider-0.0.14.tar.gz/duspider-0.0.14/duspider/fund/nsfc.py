# -*- coding: utf-8 -*-
# @project: duspider
# @Author：dyz
# @date：2024/1/8 9:56
import ssl
import json
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict
import urllib3

import httpx
import requests
from duspider.exceptions import RequestError
from pydantic import BaseModel

from tqdm import tqdm

from duspider.tools import get_ua, decrypt, re_quality

from duspider.base import Spider

urllib3.disable_warnings()
logger = logging.getLogger(__file__)


class NSFCHit(BaseModel):
    uid: str  # 数据 id
    ratify_no: str  # 批准号
    project_name: str  # 项目名称
    project_category: str = ''  # 项目类别
    project_leader: str = ''  # 负责人
    approval_year: str = ''  # 批准年份
    project_funding: str = ''  # 资助经费
    project_unit: str = ''  # 依托单位
    project_keyword_c: str = ''  # 项目关键词中文
    project_keyword_e: str = ''  # 项目关键词英文
    project_apply_code: str = ''  # 学部学科
    report_year: str = ''  # 结题年份
    start_date: str = ''  # 开始年份
    end_date: str = ''  # 结束年份
    has_report: bool = False  # 是否有报告
    project_abstract_c: str = ''  # 摘要 中文
    project_abstract_e: str = ''  # 摘要 英文
    info: Dict = None  # 返回原数据
    data: Dict = None  # 返回检索与详情的原数据
    url: str = None


    def __json(self, val):
        if isinstance(val, (list, dict)):
            return json.dumps(val, ensure_ascii=False)
        return val

    def to_db(self) -> dict:
        return {k: self.__json(v) for k, v in self.dict().items()}


class NSFC(Spider):
    """
    国自然基金: https://kd.nsfc.cn/finalProjectInit?advanced=true
    """

    def __init__(self, start_year=1986, end_year=None, path=None, sem=10):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Authorization': 'Bearer undefined',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'DNT': '1',
            'Origin': 'https://kd.nsfc.gov.cn',
            'Referer': 'https://kd.nsfc.gov.cn/finalProjectInit?advanced=true',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': get_ua(),
            'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        super().__init__()
        self.path = path
        self.query_url = 'https://kd.nsfc.cn/api/baseQuery/completionQueryResultsData'
        self.info_url = 'https://kd.nsfc.cn/api/baseQuery/conclusionProjectInfo/'
        self.img_url = 'https://kd.nsfc.cn/api/baseQuery/completeProjectReport'
        self.start_year = start_year or 1986

        self.client = requests.Session()
        self.client.headers = self.headers
        self.key = 'SecretIs'  # 2024-1-8 日维护 密文
        date = datetime.now()
        self.end_year = end_year or date.year
        self.month = end_year or date.month
        self.size = 10
        self.projectType = {
            "218": "面上项目",
            "220": "重点项目",
            "339": "重大研究计划",
            "579": "联合基金项目",
            "630": "青年科学基金项目",
            "631": "地区科学基金项目",
            "649": "专项基金项目",
            "80": "数学天元基金项目",
        }
        self.dict = {
            "A": 33,
            "B": 9,
            "C": 21,
            "D": 7,
            "E": 13,
            "F": 7,
            "G": 4,
            "H": 35,
        }

    def sem(self, resp):
        if '503 Service Temporarily Unavailable' in resp.text:
            self.headers
            return False
        return True

    def reset_hraders(self):
        headers = self.headers
        headers['User-Agent'] = get_ua()
        self.client.headers = headers

    async def post(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = self.client.post(url,
                                        timeout=self.timeout,
                                        verify=False,
                                        **kwargs)
                if self.sem(resp):
                    return resp
                else:
                    time.sleep(0.5)
                    self.reset_hraders()
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''

    async def get(self, url, **kwargs):
        for i in range(self.max_retry):
            try:
                resp = self.client.get(url,
                                       timeout=self.timeout,
                                       verify=False,
                                       **kwargs)

                if self.sem(resp):
                    return resp
                else:
                    time.sleep(0.5)
                    self.reset_hraders()
            except Exception as err:
                time.sleep(0.5)
                if i == self.max_retry - 1:
                    raise RequestError(url, err=err, retry=i)
        return ''

    async def all(self, start_year=None, end_year=None):
        """所有结题项目"""
        start = start_year or self.start_year
        end = end_year or self.end_year

        for year in range(start, end):
            for k1, v1 in self.projectType.items():
                for k, v in self.dict.items():
                    desc = f'年份:{year}-{v1}-{k}'
                    for i in tqdm(range(1, v + 1), desc=desc):
                        if len(str(i)) == 1:
                            code = f'{k}0{i}'
                        else:
                            code = f'{k}{i}'
                        json_data = {
                            'code': code,
                            'fuzzyKeyword': '', 'complete': True, 'isFuzzySearch': False,
                            'conclusionYear': f'{year}',
                            'dependUnit': '', 'keywords': '',
                            'pageNum': 0, 'pageSize': self.size,
                            'personInCharge': '', 'projectName': '',
                            'projectType': k1,
                            'subPType': '', 'psPType': '', 'ratifyNo': '', 'ratifyYear': '',
                            'order': 'enddate', 'ordering': 'desc',
                            'codeScreening': '', 'dependUnitScreening': '', 'keywordsScreening': '',
                            'projectTypeNameScreening': '',
                        }
                        res = await self.post(self.query_url, json=json_data)
                        if res.status_code == 200:
                            resp = decrypt(res.text)
                            resp = json.loads(resp)
                            count = resp['data']['itotalRecords']
                            if count > 0:
                                async for row in self.pages(year, v1, code, count, resp['data'], json_data):
                                    yield row
                        else:
                            print(self.query_url)
                            print(json_data)
                            print(res.text)
                            logger.error(f'desc: {desc}, err: [{res.status_code}]')

    async def pages(self, year, v1, code, count, data, json_data):
        pages = int(count / self.size) + 1
        async for row in self.parse_list(v1, data):  # 解析第一页数据
            yield row
        page = 1
        if pages > 1:
            for page in tqdm(range(page, pages), desc=f'{year}-{v1}-{code}'):  # 翻页
                json_data['pageNum'] = page + 1
                res = await self.post(self.query_url, json=json_data)
                if res.status_code == 200:
                    print('a',res,res.text)
                    resp = decrypt(res.text)
                    print(resp)
                    resp = json.loads(resp)
                    # res = res.json()
                    data = resp['data']
                    async for row in self.parse_list(v1, data):  # 解析翻页数据
                        yield row
                else:
                    logger.error(f'page: {page}, err: [{res.status_code}]')

    async def parse_list(self, category, data):
        for row in data['resultsData']:
            pid = row[0]
            approval_year = row[7]  # 批准年份
            report_year = row[15]  # 结题年份
            yield await self.get_info(pid, approval_year, report_year, category, row)

    async def get_info(self, pid, approval_year, report_year, category, data) -> NSFCHit:
        url = f"{self.info_url}{pid}"
        res = await self.post(url)
        row = res.json()['data']
        name = row['projectName']
        item = NSFCHit(uid=pid,ratify_no=row['ratifyNo'], project_name=name)

        item.project_category = category
        item.project_leader = row['projectAdmin']

        item.approval_year = approval_year
        item.data = data
        item.info = row
        item.url = url
        item.project_funding = row['supportNum']
        item.project_unit = row['dependUnit']
        item.project_apply_code = row['code']
        item.project_abstract_c = row['projectAbstractC']
        item.project_abstract_e = row['projectAbstractE']
        item.project_keyword_c = row['projectKeywordC']
        item.project_keyword_e = row['projectKeywordE']
        item.report_year = report_year

        research_scope = row['researchTimeScope']
        start_date, end_date = research_scope.split('到')
        start_date = start_date.split(' ')[0]
        end_date = end_date.split(' ')[0]
        item.start_date = start_date
        item.end_date = end_date

        item.has_report = True if str(row['hasReport']).lower() == 'true' else False

        return item

    async def get_images(self, uid) -> int:
        """下载结题报告图片
        return 图片总数量
        """
        index = 1
        abs_path = Path(self.path, uid)
        if not abs_path.exists():
            abs_path.mkdir()
        while True:
            data = {
                'id': uid,
                'index': str(index),
            }
            resp = await self.post(self.img_url, data=data, headers=self.headers)
            url = resp.json()['data']['url']
            sta = await self._download_img(abs_path, index, url)
            if not sta:
                return index
            index += 1

    async def _download_img(self, abs_path, index, url) -> bool:
        href = f"https://kd.nsfc.gov.cn{url}"
        res = await self.get(href)
        a_file = Path(abs_path, f'{index}_.png')
        b_file = Path(abs_path, f'{index}.png')
        if res.headers['Content-Type'] == 'image/png':
            with open(a_file, 'wb') as f:
                f.write(res.content)
            # 压缩图片
            re_quality(a_file, b_file)
            a_file.unlink()  # 删除原图
            return True
        return False

    async def t1(self):
        async for row in self.all(start_year=2022):
            print(row)
            input('>')


if __name__ == '__main__':
    nsfc = NSFC()
    import asyncio

    asyncio.run(nsfc.t1())
