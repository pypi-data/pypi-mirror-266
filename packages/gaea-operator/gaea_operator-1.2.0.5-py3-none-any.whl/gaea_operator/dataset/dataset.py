#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/21
# @Author  : yanxiaodong
# @File    : dataset_concat.py
"""
import json
import os
from abc import ABCMeta, abstractmethod
from typing import Any, List, Union, Tuple

import bcelogger
from windmillclient.client.windmill_client import WindmillClient

from gaea_operator.utils import find_upper_level_folder, write_file


class Dataset(metaclass=ABCMeta):
    """
    A dataset for data processing.
    """
    decompress_output_uri = "/root/dataset"
    usages = ["", ""]

    def __init__(self, windmill_client: WindmillClient, work_dir: str, extra_work_dir: str = None):
        self.windmill_client = windmill_client
        self.work_dir = work_dir
        self.extra_work_dir = extra_work_dir
        self.labels = []
        self.image_set = set()
        self.image_prefix_path = ""
        self.label_file_path = "labels.json"
        assert len(self.usages) == 2, "Dataset mode keys length must equal 2"

    def reset(self):
        """
        Reset attribute variable.
        """
        pass

    def concat_dataset(self,
                       dataset_name: str,
                       output_dir: str,
                       usage: Union[str, Tuple],
                       base_dataset_name: str = None,
                       save_label: bool = False):
        """
        Concat dataset from artifact.
        """
        self.reset()
        # 处理base dataset name
        base_raw_data_list = []
        if base_dataset_name is not None and len(base_dataset_name) > 0:
            bcelogger.info(f"Concat base dataset from dataset name {base_dataset_name}")
            response = self.windmill_client.get_artifact(name=base_dataset_name)
            filesystem = self.windmill_client.suggest_first_filesystem(workspace_id=response.workspaceID,
                                                                       guest_name=response.parentName)
            base_uri = self.windmill_client.build_base_uri(filesystem=filesystem)
            base_paths = [os.path.relpath(_path, base_uri).rstrip('/') for _path in response.metadata["paths"]]

            bcelogger.info(f"Concat base dataset from path {base_paths}")
            base_raw_data_list = self._get_annotation(paths=base_paths,
                                                      base_uri=base_uri,
                                                      usage=usage,
                                                      work_dir=self.extra_work_dir)

        bcelogger.info(f"Concat dataset from dataset name {dataset_name}")
        response = self.windmill_client.get_artifact(name=dataset_name)
        write_file(json.loads(response.raw_data), output_dir=output_dir)
        filesystem = self.windmill_client.suggest_first_filesystem(workspace_id=response.workspaceID,
                                                                   guest_name=response.parentName)
        base_uri = self.windmill_client.build_base_uri(filesystem=filesystem)
        paths = [os.path.relpath(_path, base_uri).rstrip('/') for _path in response.metadata["paths"]]
        bcelogger.info(f"Concat dataset from path {paths}")

        raw_data_list = self._get_annotation(paths=paths, base_uri=base_uri, usage=usage, work_dir=self.work_dir)

        raw_data_list += base_raw_data_list
        raw_data = self._concat_annotation(raw_data_list=raw_data_list)
        self._write_annotation(output_dir=output_dir,
                               file_name=usage if isinstance(usage, str) else usage[0],
                               raw_data=raw_data)

        self._warmup_image_meta()

        if usage == self.usages[0] or save_label:
            self._write_category(output_dir=output_dir)

    @abstractmethod
    def _get_annotation(self, paths: List, base_uri: str, usage: str, work_dir: str) -> List:
        pass

    @abstractmethod
    def _concat_annotation(self, raw_data_list: List):
        pass

    @abstractmethod
    def _write_annotation(self, output_dir: str, file_name: str, raw_data: Any):
        pass

    def _write_category(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, self.label_file_path)
        with open(file_path, "w") as fp:
            json.dump(self.labels, fp)

    def _file_name_cvt_abs(self, image_file: str, path: str, fs_prefix: str, level: int, work_dir: str):
        if image_file.startswith(fs_prefix):
            file = image_file.replace(fs_prefix, work_dir)
            return file
        if os.path.isabs(image_file):
            return image_file
        else:
            return os.path.join(find_upper_level_folder(path, level), self.image_prefix_path, image_file)

    def _warmup_image_meta(self):
        dirs = [os.path.dirname(filepath) for filepath in self.image_set]
        dirs = set(dirs)
        for dir in dirs:
            os.listdir(dir)
