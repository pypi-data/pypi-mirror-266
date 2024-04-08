#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: tm
import platform
import cpuinfo
class Tools():
    """
    工具类
    """
    def __new__(cls, *a, **k):
        return object.__new__(cls)
    def __init__(self,*args, **kwargs) -> None:...
    def __del__(self) -> None:...

    def getPlatformInfo(self,*fa, **fk) -> None:
        # 获取操作系统名称
        os_name = platform.system()
        # 获取操作系统版本号
        os_version = platform.release()
        # 获取 CPU 的相关信息，包括序列号。
        cpu_info = cpuinfo.get_cpu_info()
        # 打印操作系统信息
        print("Operating System:", os_name)
        print("Version:", os_version)
        print(cpu_info)
