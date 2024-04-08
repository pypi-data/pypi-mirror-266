#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/6
# @Author  : yanxiaodong
# @File    : compress.py
"""
import os
from typing import List, Union, Tuple
import shutil

import bcelogger


def is_compressed_file(file: str):
    """
    Check if the file is compressed.
    """
    compressed_extensions = ['.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.gz', '.bz2', '.xz']
    file_extension = os.path.splitext(file)[1]
    return file_extension in compressed_extensions


def decompress(filepath: str, ext: str, output_uri: str = "./"):
    """
    Extract the compressed file.
    """
    file_list = []
    if filepath.startswith("/"):
        target_path = os.path.join(output_uri, filepath[1:])
    else:
        target_path = os.path.join(output_uri, filepath)
    shutil.unpack_archive(output_uri, target_path)
    for root, dirs, files in os.walk(target_path):
        for file in files:
            if file.endswith(ext):
                absolute_file = os.path.join(root, file)
                file_list.append(absolute_file)

    return file_list


def get_filepaths_in_archive(path: str, output_uri: str, target: Union[str, Tuple]) -> List[str]:
    """
    Traverse the file directory recursively.
    """
    file_list = []
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                absolute_file = os.path.join(root, file)
                if is_compressed_file(absolute_file):
                    if isinstance(target, str):
                        file_list.extend(decompress(absolute_file, target, output_uri))
                    else:
                        for t in target:
                            file_list.extend(decompress(absolute_file, t, output_uri))
                else:
                    if isinstance(target, str):
                        if file.endswith(target):
                            file_list.append(absolute_file)
                    else:
                        for t in target:
                            if file.endswith(t):
                                file_list.append(absolute_file)
    elif os.path.isfile(path):
        if is_compressed_file(path):
            file_list.extend(decompress(path, target, output_uri))
        else:
            if isinstance(target, str):
                if path.endswith(target):
                    file_list.append(path)
            else:
                for t in target:
                    if path.endswith(t):
                        file_list.append(path)
    else:
        raise ValueError(f"Path {path} is not a file or directory")

    bcelogger.info(f"Found {len(file_list)} target file is {file_list}")

    return file_list