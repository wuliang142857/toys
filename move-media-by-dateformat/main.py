#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8 ff=unix ft=python

import sys
import os
import shutil
from argparse import ArgumentParser
import arrow
import logging

# 定义一个 Formatter 对象，用于设置日志格式
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s',
                              datefmt='%Y%m%d %H:%M:%S')

# 创建一个 StreamHandler 对象，用于将日志输出到 stdout
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

# 获取或创建一个 Logger 对象
logger = logging.getLogger("parallel-imposm")
logger.setLevel(logging.INFO)  # 设置日志级别
logger.addHandler(handler)  # 添加 Handler

def move(input_file, dst):
    creation_time = os.path.getctime(input_file)
    target_dir = os.path.join(dst, arrow.get(creation_time).format("YYYY-MM"), arrow.get(creation_time).format("YYYY-MM-DD"))
    logger.info(f"{input_file} -> {target_dir}")

    # shutil.move(src, dst)

def main():
    parser = ArgumentParser(prog="move-media-by-dateformat", description="移动文件到指定目录")
    parser.add_argument("--src", required=True, type=str, dest="src", help="源文件路径")
    parser.add_argument("--dst", required=True, type=str, dest="dst", help="目标路径")
    
    argument = parser.parse_args()
    src = argument.src
    dst = argument.dst
    
    for root, dirnames, filenames in os.walk(src):
        for filename in filenames:
            srcFilePath = os.path.join(root, filename)
    

if __name__ == '__main__':
    main()
