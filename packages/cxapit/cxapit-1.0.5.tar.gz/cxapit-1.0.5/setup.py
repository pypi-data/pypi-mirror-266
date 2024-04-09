#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: tm
# Description:

from setuptools import setup, find_packages,Extension
import os
import re

script_dir = os.path.dirname(os.path.realpath(__file__))
# 定义要包含的共享库文件
package_data = {
    "": ["*.so"]
}

version_dir=script_dir+"/Version"

def increment_version(version_str):
    # 使用正则表达式提取主版本号、次版本号和修订号
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if match:
        major, minor, patch = match.groups()
        # 将次版本号加一
        patch = int(patch) + 1
        # 更新版本号
        new_version = f"{major}.{minor}.{patch}"
        return new_version
    else:
        raise ValueError("Invalid version format")

Versionf=open(version_dir,'r')
current_version=Versionf.read().strip()

# 自动增加版本号
new_version = increment_version(current_version)

with open(version_dir,'w') as f:
    f.write(new_version)
    f.flush()

setup(
    name = 'cxapit',
    version = new_version,
    package_data=package_data,
    keywords='H',
    description = 'A Python client for the Bacalha public API',
    license = 'License',
    url = 'https://github.com/bacalhau-project/bacalhau/tree/main',
    author = 'bacalha',
    author_email = 'xm6798121@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'requests>=2.19.1',
        "py-cpuinfo>=9.0.0",
        "ntplib>=0.4.0",
        ],
)