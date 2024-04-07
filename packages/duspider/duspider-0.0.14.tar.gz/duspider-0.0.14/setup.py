# -*- coding: utf-8 -*-
# @Time    : 2021/9/1 10:05
# @Author  : DYZ
# @Software: PyCharm

from pathlib import Path

from setuptools import find_packages, setup

# 提供一些有用的信息
NAME = 'duspider'  # Python 包的名称，即在 pip install 时后面跟的包名
VERSION = '0.0.14'  # 包的版本，每次上传到 PyPI 都需要改变这个版本号，否则只会往存储空间增加新内容，无法达到预期
DESCRIPTION = "Commonly used spiders"  # 关于该包的剪短描述

readme = Path('README.md')

if readme.exists():  # 如果需要，可以加入一段较长的描述，比如读取 README.md，该段长描述会直接显示在 PyPI 的页面上
    with open(readme, encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = DESCRIPTION
AUTHOR = 'DYZ'  # 留下大名
AUTHOR_EMAIL = 'duyuchau@gmail.com'  # 留下邮箱
LICENSE = 'MIT'  # 定义合适自己的许可证，实在不知道，那就 MIT 吧
PLATFORMS = [  # 支持的平台，如果所有平台都支持，可以填 all
    'all',
]


ALL = [  # 很多时候，我自己写的包都要依赖第三方，所以可以把依赖包定义在这里，这样的 pip install 自己包的时候，顺便把这些依赖包都装上了
    'httpx',
    'parsel',
    'requests',
    'parsel',
    'pydantic',
    'httpx[http2]',
]
# CONSOLE_SCRIPT = 'my-cmd=my_pkg.my_cmd:main'                  # 如果想在 pip install 之后自动生成一个可执行命令，就靠它了:


# 需要的信息就在 setup() 中加上，不需要的可以不加
setup(
    name=NAME,
    version=VERSION,
    description=(
        DESCRIPTION
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    platforms=PLATFORMS,
    install_requires=ALL,
)
