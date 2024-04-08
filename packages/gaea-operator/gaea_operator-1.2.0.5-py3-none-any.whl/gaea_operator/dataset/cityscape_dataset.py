#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/17
# @Author  : yanxiaodong
# @File    : imagenet_dataset.py
"""
import os
from typing import List, Any

import bcelogger
from windmillclient.client.windmill_client import WindmillClient

from .dataset import Dataset
from gaea_operator.utils import get_filepaths_in_archive


class CityscapesDataset(Dataset):
    """
    Cityscapes Dataset
    """
    usages = ["train.txt", "val.txt"]

    def __init__(self, windmill_client: WindmillClient, work_dir: str):
        super().__init__(windmill_client=windmill_client, work_dir=work_dir)

        self.image_prefix_path = ""

    def _get_annotation(self, paths: List, base_uri: str, usage: str, work_di: str):
        annotation_file_list = []
        for path in paths:
            path = os.path.join(self.work_dir, path)
            annotation_file_list = get_filepaths_in_archive(path, self.decompress_output_uri, usage)

        bcelogger.info(f"[{usage.capitalize()}] annotation file list is: {annotation_file_list}")

        raw_data_list = []
        label_list = []
        for file in annotation_file_list:
            text_data = open(file, "r").read()
            raw_data = text_data.strip("\n").split("\n")

            bcelogger.info(f"Parse annotation file {file}, image num is {len(raw_data)}")

            for idx in range(len(raw_data)):
                img_file, label_file = raw_data[idx].rsplit(" ", 1)
                img_file = self._file_name_cvt_abs(img_file, file, base_uri, 1, work_di)
                label_file = self._file_name_cvt_abs(label_file, file, base_uri, 1, work_di)
                raw_data[idx] = img_file + " " + label_file

            raw_data_list.append(raw_data)

            label_data = open(os.path.join(os.path.dirname(file), "labels.txt"), "r").read().strip("\n").split("\n")
            label_list.append(label_data)

        if len(raw_data_list) > 1:
            raw_data_imagenet = self._cityscapes_data_raw_concat(raw_data_list, label_list)
        elif len(raw_data_list) == 1:
            raw_data_imagenet = raw_data_list[0]
            self.labels = [{"id": idx, "name": name} for idx, name in enumerate(label_list[0])]
        else:
            raw_data_imagenet = None

        return raw_data_imagenet

    def _cityscapes_data_raw_concat(self, raw_data: List[List], label_list: List[List]):
        label_name = self._category_valid(label_list)

        raw_data_cityscapes = []

        for idx, data in enumerate(raw_data):
            old2new_cat_id = {}
            for inner_idx, label in enumerate(label_list[idx]):
                if label != label_name[inner_idx]:
                    old2new_cat_id[inner_idx] = label_name.index(label)
            for item in data:
                raw_data_cityscapes.append(item)

        return raw_data_cityscapes

    def _write_annotation(self, output_dir: str, file_name: str, raw_data: Any):
        if raw_data is None:
            return
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w") as fp:
            for item in raw_data:
                fp.write(item + "\n")

    def _category_valid(self, label_list: List[List]):
        lengths = [len(label) for label in label_list]

        if len(set(lengths)) == 1:
            bcelogger.info(f"The number of labels is {lengths[0]}")
            for idx in range(1, len(lengths)):
                for inner_idx, label in enumerate(label_list[idx]):
                    if label != label_list[0][inner_idx]:
                        raise ValueError(f"The labels name is not equal, please check {label_list}")
            self.labels = [{"id": idx, "name": name} for idx, name in enumerate(label_list[0])]
            return label_list[0]
        else:
            raise ValueError(f"The number of labels is not equal, please check {label_list}")

