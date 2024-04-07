# -*- coding: utf-8 -*-
"""
# @项目名称 :zsx_pack
# @文件名称 :setup.py
# @作者名称 :zsx
# @日期时间 :2024/4/3 17:06
# @文件介绍 :
"""
import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zsx_pack",
    version="1.0.0",
    author="zsx",
    author_email="17630583910@163.com",
    description="自用包，主要是为了logger无法屏蔽第三方包日志而开发的",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ziyueguyi/zsx_pack",
    project_urls={
        "Bug Tracker": "https://github.com/ziyueguyi/zsx_pack",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
    ],
    package_dir={"": "logger"},
    python_requires=">=3.6",
)
