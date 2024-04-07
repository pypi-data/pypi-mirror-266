#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: tm
# Description:

from setuptools import setup, find_packages

setup(
    name = 'OpsApi',
    version = '0.0.1',
    keywords='tm',
    description = 'a library for tm Developer',
    license = 'MIT License',
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