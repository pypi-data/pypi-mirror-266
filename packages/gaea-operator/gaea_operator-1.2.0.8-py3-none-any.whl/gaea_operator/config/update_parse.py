# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
modify parse.yaml
Authors: zhouwenlong(zhouwenlong01@baidu.com)
         wanggaofei(wanggaofei03@baidu.com)
Date:    2023-03-16
"""
import yaml
import os
import argparse
import bcelogger

KEY_OUTPUTS = 'outputs'
KEY_MODEL_NAME = 'model_name'

class ParseYamlConfig(object):
    """
    解析修改模型包 parse.yaml
    """
    def __init__(self, yaml_name):
        """
            初始化YAML数据类，用于读取和解析指定名称的YAML文件。
        
        Args:
            yaml_name (str): YAML文件名，不包含路径信息。
        
        Returns:
            None.
        """
        self.yaml_data = self.get_yaml(yaml_name)

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

    def modify_categories(self, categories : list, modify_model_name: str = ""):
        """
            modify categories by model-name
        """
        class_field = self.yaml_data.get(KEY_OUTPUTS , None)
        if class_field is None:
            raise ValueError("outputs is None")
        
        ensemble_field = class_field[0]
        fields_map = ensemble_field.get("fields_map", None)
        if fields_map is None:
            raise ValueError("fields_map is None")

        for single_map in fields_map:
            model_name = single_map.get(KEY_MODEL_NAME, None)
            if model_name is None:
                raise ValueError("model_name is None")
            
            model_name = model_name.split('|')[0]
            if len(modify_model_name) == 0 or model_name == modify_model_name:
                new_categories = []
                for cidx, class_name in enumerate(categories) :
                    new_categories.append({
                        "name": class_name["name"],
                        "id": class_name["id"]
                    })

                single_map["categories"] = new_categories
                bcelogger.info('set categories. model_name: {} num: {}'.format(model_name, len(new_categories)))

    def modify_ensemble_name(self, ensemble_name: str):
        """
            modify ensemble name
        """
        if KEY_OUTPUTS in self.yaml_data:
            for _, v in enumerate(self.yaml_data[KEY_OUTPUTS]):
                if KEY_MODEL_NAME in v and 'ensemble' in v[KEY_MODEL_NAME]:
                    v[KEY_MODEL_NAME] = ensemble_name
                    bcelogger.info('modify ensemble name: {}'.format(ensemble_name))
        else:
            bcelogger.error('do NOT find key in parse.yaml: {}'.format(KEY_OUTPUTS))

    def save_yaml(self, yaml_name):
        """
        将字典数据保存为YAML格式的文件。
        
        Args:
            yaml_name (str): YAML文件名，包含路径。
        
        Returns:
            None; 无返回值，直接写入文件。
        """
        with open(yaml_name, 'w', encoding='utf-8') as f:
            yaml.dump(self.yaml_data, f, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    cfg = ParseYamlConfig('./parse.yaml')

    # 1. set ensemble name
    cfg.modify_ensemble_name('abc-ensemble')

    # 2. set categories
    categories = ['label1', 'label2']
    cfg.modify_categories(categories)

    # 3. save
    cfg.save_yaml('./output-parse.yaml')