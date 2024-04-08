#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/21
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from .coco_dataset import CocoDataset
from .imagenet_dataset import ImageNetDataset

__all__ = ["CocoDataset", "ImageNetDataset"]