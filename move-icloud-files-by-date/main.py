#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8 ff=unix ft=python

import sys
import os
import shutil
from argparse import ArgumentParser
import logging
from uuid import uuid4

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

def get_file_creation_time(file_path):
    day = os.path.basename(os.path.dirname(file_path))
    month = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
    year = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(file_path))))
    return (year, month, day)

def move(input_file, dst, dry_run = False):
    year, month, day = get_file_creation_time(input_file)
    target_dir = os.path.join(dst, f"{year}-{month}", f"{year}-{month}-{day}")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, 0o755)
    target_file = os.path.join(target_dir, os.path.basename(input_file))
    if os.path.exists(target_file):
        name, ext = os.path.splitext(input_file)
        target_file = f"{target_file}-{str(uuid4())}{ext}"
        
    logger.info(f"{input_file} -> {target_file}")

    if not dry_run:
        shutil.move(input_file, target_file)

def main():
    parser = ArgumentParser(prog="move-icloud-files-by-date", description="移动文件到指定目录")
    parser.add_argument("--src", required=True, type=str, dest="src", help="源文件路径")
    parser.add_argument("--dst", required=True, type=str, dest="dst", help="目标路径")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run", help="仅打印日志，不执行移动操作")
    
    argument = parser.parse_args()
    src = os.path.realpath(argument.src)
    dst = argument.dst
    dry_run = argument.dry_run
    
    for root, dirnames, filenames in os.walk(src):
        for filename in filenames:
            srcFilePath = os.path.join(root, filename)
            move(srcFilePath, dst, dry_run)
    

if __name__ == '__main__':
    main()
