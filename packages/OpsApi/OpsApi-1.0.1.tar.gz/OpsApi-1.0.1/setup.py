#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: tm
# Description:

from setuptools import setup, find_packages,Extension

# 定义要包含的共享库文件
package_data = {
    "": ["*.so"],  # 包含当前目录下的所有 .so 文件
}

setup(
    name = 'OpsApi',
    version = '1.0.1',
    package_data=package_data,
    keywords='tm',
    description = 'a library for tm Developer',
    license = 'License',
    url = 'https://github.com/tm',
    author = 'Tommi',
    author_email = 'xm6798121@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'requests>=2.19.1',
        ],
)