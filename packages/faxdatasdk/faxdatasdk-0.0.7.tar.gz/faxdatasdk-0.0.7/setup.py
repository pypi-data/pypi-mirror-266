# !/usr/bin/env python
# -*- coding=utf-8 -*-,

import os
import sys
import re
from setuptools import setup, find_packages


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_version():
    scope = {}
    version = '0.0.1'
    version_file = os.path.join(THIS_FOLDER, "faxdatasdk", "version.py")
    if os.path.exists(version_file):
        with open(version_file) as fp:
            exec(fp.read(), scope)
        version = scope.get('__version__', '0.0.1')
    return version


def get_long_description():
    with open(os.path.join(THIS_FOLDER, 'README.md'), 'rb') as f:
        long_description = f.read().decode('utf-8')
    return long_description


def _parse_requirement_file(path):
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        requirements = [line.strip() for line in f if line.strip()]
    return requirements


def get_install_requires():
    requirement_file = os.path.join(THIS_FOLDER, "requirements.txt")
    return _parse_requirement_file(requirement_file)


setup(
    name="faxdatasdk",
    version=get_version(),
    description="Data SDK for stock analysis.",
    packages=find_packages(exclude=("tests",)),
    author="PinkQuant",
    author_email="tickertrading@163.com",
    maintainer="topbip",
    maintainer_email="pinkquant@163.com",
    license='Apache License v2',
    package_data={'': ['*.*']},
    url="https://www.faxframework.com",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    install_requires=get_install_requires(),
    zip_safe=False,
    platforms=["all"],
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
    ],
)
