# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
modify model config.pbtxt/parse.yaml in package step
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-02-29
"""

import yaml
import os
import bcelogger
from typing import Dict

from .update_pbtxt import ModelConfig
from .update_parse import ParseYamlConfig
from gaea_operator.utils import find_dir

KEY_PREPROCESS = 'preprocess'
KEY_MODEL = 'model'
KEY_ENSEMBLE = 'ensemble'
KEY_POSTPROCESS = 'postprocess'
KEY_PBTXT_NAME = 'config.pbtxt'
KEY_PARSE_NAME = 'parse.yaml'
KEY_MAX_BATCH_SIZE = 'max_batch_size'


class ModifyEnsembleFile(object):
    """
    解析修改模型包 config.pbtxt
    """

    def __init__(self,
                 ensemble_model_uri: str,
                 model_config: Dict
                 ):
        """
            初始化YAML数据类
        """
        self.ensemble_model_uri = ensemble_model_uri
        self.model_name_pairs, self.model_version_pairs = self.get_model_name_pairs(model_config)

    def get_model_name_pairs(self, model_config: Dict):
        """
            old_name -> new_name
        """
        model_name_pairs = {}
        model_version_pairs = {}
        for k, v in model_config.items():
            model_name_pairs[k] = v['localName']
            model_version_pairs[k] = v['artifact']['version']
        return model_name_pairs, model_version_pairs

    def modify_ensemble(self):
        """
            modify ensemble model-name
        """
        aim_files = self.retrive_path(find_dir(self.ensemble_model_uri), [KEY_PBTXT_NAME])
        if len(aim_files) > 0:
            ensemble_pbtxt_name = aim_files[0]
            ensemble_config = ModelConfig._create_from_file(ensemble_pbtxt_name)
            ensemble_config.set_ensemble_step_model_name_and_version(self.model_name_pairs, self.model_version_pairs)
            ensemble_config.write_config_to_file(ensemble_pbtxt_name)
        else:
            bcelogger.error('do NOT find {} in {}'.format(KEY_PBTXT_NAME, self.ensemble_model_uri))

    def retrive_path(self, path, exts):
        """
        从指定路径中递归搜索，返回指定扩展名的文件列表

        Args:
        path (str): 指定的文件目录路径
        exts (list[str]): 文件扩展名列表

        Returns:
        list[str]: 返回包含文件路径的列表

        """
        aim_files = []
        n = 0
        for home, dirs, files in os.walk(path):
            for _, f in enumerate(files):
                if f in exts and not f.startswith("._"):
                    w_name = os.path.join(home, f)
                    n += 1
                    bcelogger.info("FIND" + str(n) + ":" + w_name)
                    aim_files.append(w_name)

        return aim_files


class ModifyPackageFiles(object):
    """
    解析修改模型包 parse.yaml
    """

    def __init__(self,
                 modify_model_names: dict,
                 metadata: dict = {},
                 ensemble_model_uri: str = None,
                 ensemble_local_name: str = None
                 ):
        """
            初始化YAML数据类
        """
        # 1. read parameter of modify
        algo_param_dict = self.get_algorithm_parameters(metadata)
        self.eval_width = int(algo_param_dict['evalWidth']) if 'evalWidth' in algo_param_dict else 0
        self.eval_height = int(algo_param_dict['evalHeight']) if 'evalHeight' in algo_param_dict else 0
        self.max_batch_size = int(algo_param_dict['inferenceMaxBatchSize']) \
            if 'inferenceMaxBatchSize' in algo_param_dict else 0
        self.max_box_count = int(algo_param_dict['maxBoxNum']) if 'maxBoxNum' in algo_param_dict else 0
        self.categories = self.get_yaml_categories(metadata)

        self.ensemble_model_uri = ensemble_model_uri
        self.modify_model_names = modify_model_names
        self.ensemble_local_name = ensemble_local_name

    def get_algorithm_parameters(self, metadata: dict):
        """
        get algorithm parameter dict from meta.yaml
        """
        yaml_data = metadata

        if 'algorithmParameters' in yaml_data:
            alg_param = yaml_data['algorithmParameters']
            return alg_param.copy()
        return {}

    def get_yaml_categories(self, metadata: dict):
        """
            获取YAML中的类别列表，返回一个列表。
        每个元素都是一个字符串，代表一个类别名称。
        
        Returns:
            list (str) - 类别列表，每个元素为一个字符串，代表一个类别名称。
        """
        categories = []
        yaml_data = metadata

        if 'labels' in yaml_data:
            categories = yaml_data['labels']
        return categories

    def get_yaml(self, yaml_name):
        """
            read parse.yaml
        """
        if not os.path.exists(yaml_name):
            raise FileNotFoundError(yaml_name)
        with open(yaml_name, 'r', encoding='utf-8') as f:
            file_data = f.read()
            yaml_data = yaml.load(file_data, Loader=yaml.FullLoader)
            return yaml_data

    def retrive_path(self, path, exts):
        """
        从指定路径中递归搜索，返回指定扩展名的文件列表
        
        Args:
        path (str): 指定的文件目录路径
        exts (list[str]): 文件扩展名列表
        
        Returns:
        list[str]: 返回包含文件路径的列表
        
        """
        aim_files = []
        n = 0
        for home, dirs, files in os.walk(path):
            for _, f in enumerate(files):
                if f in exts and not f.startswith("._"):
                    w_name = os.path.join(home, f)
                    n += 1
                    bcelogger.info("FIND" + str(n) + ":" + w_name)
                    aim_files.append(w_name)

        return aim_files

    def modify_ppyoloe(self, output_uri: str = None):
        """
        for ppyoloe
        """
        # 1. modify pbtxt
        for model_type, models in self.modify_model_names.items():
            if model_type == KEY_PREPROCESS:
                # 1. preproc node modify width
                for m in models:
                    aim_files = self.retrive_path(find_dir(
                        os.path.join(self.ensemble_model_uri, m)), [KEY_PBTXT_NAME])
                    if len(aim_files) > 0:
                        preproc_pbtxt_name = aim_files[0]
                        preproc_config = ModelConfig._create_from_file(preproc_pbtxt_name)
                        preproc_config.set_preproc_width_height(idx=0, width=self.eval_width, \
                                                                height=self.eval_height, is_nhwc=True)
                        preproc_config.write_config_to_file(preproc_pbtxt_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PBTXT_NAME, m))
            elif model_type == KEY_MODEL:
                # 2. model node modify max_batch_size/max_box_count
                for m in models:
                    if output_uri is not None:
                        aim_files = [os.path.join(output_uri, KEY_PBTXT_NAME)]
                    else:
                        aim_files = self.retrive_path(find_dir(
                            os.path.join(self.ensemble_model_uri, m)), [KEY_PBTXT_NAME])
                    if len(aim_files) > 0:
                        ppyoloe_pbtxt_name = aim_files[0]
                        ppyoloe_config = ModelConfig._create_from_file(ppyoloe_pbtxt_name)
                        ppyoloe_config.set_ppyoloe_output_max_box_count(val=self.max_box_count)
                        ppyoloe_config.set_field(KEY_MAX_BATCH_SIZE, self.max_batch_size)
                        ppyoloe_config.write_config_to_file(ppyoloe_pbtxt_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PBTXT_NAME, m))

            elif model_type == KEY_POSTPROCESS:
                for m in models:
                    # 4. modify parse.yaml
                    aim_files = self.retrive_path(find_dir(
                        os.path.join(self.ensemble_model_uri, m)), [KEY_PARSE_NAME])
                    if len(aim_files) > 0:
                        parse_name = aim_files[0]
                        cfg = ParseYamlConfig(parse_name)
                        # 1. set ensemble name
                        cfg.modify_ensemble_name(self.ensemble_local_name)

                        # 2. set categories
                        cfg.modify_categories(self.categories)

                        # 3. save
                        cfg.save_yaml(parse_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PARSE_NAME, m))
            else:
                bcelogger.error('do NOT support model_type: {}'.format(model_type))

    def modify_resnet(self, output_uri: str = None):
        """
        for classify
        """
        # 1. modify pbtxt
        for model_type, models in self.modify_model_names.items():
            if model_type == KEY_PREPROCESS:
                # 1. preproc node modify width
                for m in models:
                    aim_files = self.retrive_path(find_dir(
                        os.path.join(self.ensemble_model_uri, m)), [KEY_PBTXT_NAME])
                    if len(aim_files) > 0:
                        preproc_pbtxt_name = aim_files[0]
                        preproc_config = ModelConfig._create_from_file(preproc_pbtxt_name)
                        preproc_config.set_preproc_width_height(idx=0, width=self.eval_width, \
                                                                height=self.eval_height, is_nhwc=True)
                        preproc_config.write_config_to_file(preproc_pbtxt_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PBTXT_NAME, m))
            elif model_type == KEY_MODEL:
                # 2. model node modify max_batch_size
                for m in models:
                    if output_uri is not None:
                        aim_files = [os.path.join(output_uri, KEY_PBTXT_NAME)]
                    else:
                        aim_files = self.retrive_path(find_dir(
                            os.path.join(self.ensemble_model_uri, m)), [KEY_PBTXT_NAME])
                    if len(aim_files) > 0:
                        classify_pbtxt_name = aim_files[0]
                        classify_config = ModelConfig._create_from_file(classify_pbtxt_name)
                        classify_config.set_field(KEY_MAX_BATCH_SIZE, self.max_batch_size)
                        classify_config.write_config_to_file(classify_pbtxt_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PBTXT_NAME, m))

            elif model_type == KEY_POSTPROCESS:
                for m in models:
                    # 4. modify parse.yaml
                    aim_files = self.retrive_path(find_dir(
                        os.path.join(self.ensemble_model_uri, m)), [KEY_PARSE_NAME])
                    if len(aim_files) > 0:
                        parse_name = aim_files[0]
                        cfg = ParseYamlConfig(parse_name)
                        # 1. set ensemble name
                        cfg.modify_ensemble_name(self.ensemble_local_name)

                        # 2. set categories
                        cfg.modify_categories(self.categories)

                        # 3. save
                        cfg.save_yaml(parse_name)
                    else:
                        bcelogger.error('do NOT find {} in {}'.format(KEY_PARSE_NAME, m))
            else:
                bcelogger.error('do NOT support model_type: {}'.format(model_type))


if __name__ == '__main__':
    pass
