# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
modify input train parameter yaml
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-02-29
"""

import os
import yaml
import argparse
import bcelogger

# from windmillmodelv1.client.model_api_model import ModelMetadata, InputSize

# from gaea_operator.utils import DEFAULT_META_FILE_NAME

KEY_EVAL_HEIGHT = 'eval_height'
KEY_EVAL_WIDTH = 'eval_width'
KEY_TARGET_SIZE = 'target_size'
KEY_MODEL = 'model'
KEY_TRAIN_DATASET = 'train_dataset'
KEY_VAL_DATASET = 'val_dataset'
KEY_TRANSFORMS = 'transforms'
KEY_CROP_SIZE = 'crop_size'
KEY_MODEL_TYPE = 'model_type'
KEY_PRETRAINED = 'model.backbone.pretrained'
KEY_PRETRAINED_TYPE = 'model.backbone.type'

# model_type -> [type, name]
MODEL_TYPE_NAME_DICT = {
    'ocrnet': ['HRNet_W18', 'ocrnet_hrnet_w18_ssld.pdparams']
}

def get_yaml(yaml_name):
    """
    读取指定YAML文件，并返回解析后的数据。如果读取失败，则返回None。
    
    Args:
        yaml_name (str): YAML文件的路径名。
    
    Returns:
        dict, optional: 返回一个字典类型，包含YAML文件中的内容；如果读取失败，则返回None。
    """
    with open(yaml_name) as f:
        yaml_data = yaml.load(f, Loader=yaml.Loader)
        return yaml_data
    return None

def save_yaml(yaml_data, yaml_name):
    """
    将字典数据保存为YAML格式的文件。
    
    Args:
        yaml_data (dict): 需要保存的字典数据。
        yaml_name (str): YAML文件名，包含路径。
    
    Returns:
        None; 无返回值，直接写入文件。
    """
    with open(yaml_name, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)

def set_value(yaml_data, key, val):
    """
    设置YAML数据中指定键的值，如果该键不存在则添加。如果键已经存在，将更新其值；否则，将添加一个新的键-值对。
    如果键不存在，将输出错误日志。
    
    Args:
        yaml_data (dict): YAML格式的数据，类型为字典，用于存储和修改键值对。
        key (str): 需要设置或添加的键名，类型为字符串。
        val (any): 需要设置或添加的键值，任意类型。
    
    Returns:
        None - 无返回值，直接修改传入的yamldata参数。
    
    Raises:
        None - 该函数没有引发任何异常。
    """
    if key in yaml_data:
        bcelogger.info('old val. {} -> {}'.format(key, yaml_data[key]))
        yaml_data[key] = val
        bcelogger.info('new val. {} -> {}'.format(key, yaml_data[key]))
    else:
        bcelogger.error('do NOT find key: {}'.format(key))

def get_value(yaml_data, key):
    """
    根据指定的键值获取对应的值，如果找不到则返回None。
    
    Args:
        yaml_data (dict): YAML格式的数据字典。
        key (str): 需要查询的键值。
    
    Returns:
        Union[str, int, dict, list, None]: 如果找到该键值，则返回对应的值；否则返回None。
    """
    if key in yaml_data:
        return yaml_data[key]
    else:
        bcelogger.info('do NOT find key: {}'.format(key))
        return None

def set_target_size(yaml_data, eval_width, eval_height):
    """
    设置目标大小，如果不支持该大小则报错。
    如果配置文件中存在train reader和batch transforms，并且包含batch random resize，则修改其target size为指定的大小。
    
    Args:
        yaml_data (dict): YAML格式的数据字典，包含train reader和batch transforms等信息。
        eval_width (int): 评估图像的宽度。
        eval_height (int): 评估图像的高度。
    
    Returns:
        None.
    
    Raises:
        ValueError: 如果不支持指定的目标大小。
    """
    wh_list = [int(eval_width), int(eval_height)]
    if KEY_TRAIN_DATASET in yaml_data and KEY_TRANSFORMS in yaml_data[KEY_TRAIN_DATASET]:
        for _, v in enumerate(yaml_data[KEY_TRAIN_DATASET][KEY_TRANSFORMS]):
            if KEY_TARGET_SIZE in v:
                v[KEY_TARGET_SIZE] = wh_list
                bcelogger.info('set target size: {}'.format(wh_list))

            if KEY_CROP_SIZE in v:
                v[KEY_CROP_SIZE] = wh_list
                bcelogger.info('set crop size: {}'.format(wh_list))

    if KEY_VAL_DATASET in yaml_data and KEY_TRANSFORMS in yaml_data[KEY_VAL_DATASET]:
        for _, v in enumerate(yaml_data[KEY_VAL_DATASET][KEY_TRANSFORMS]):
            if KEY_TARGET_SIZE in v:
                v[KEY_TARGET_SIZE] = wh_list
                bcelogger.info('set target size: {}'.format(wh_list))


def convert_value_type(val):
    """
        convert string to real data type
    """
    if val.isdigit():
        return int(val)
    elif val.replace('.', '', 1).isdigit():
        return float(val)
    else:
        return val

def set_multi_key_value(yaml_data, multi_key, val):
    """
        set all do not care parameter
    """
    keys = multi_key.split('.')
    config_dict = yaml_data
    for i, key in enumerate(keys):
        if key in config_dict:
            if i + 1 == len(keys):
                config_dict[key] = convert_value_type(val)
            else:
                config_dict = config_dict[key]
        else:
            bcelogger.error('do NOT find key: {} of {}'.format(key, multi_key))
            break

def set_pretrained(yaml_data, model_type, pretrained_model_path):
    """
        modify pretrained model path & type by model_type parameter
    """
    if model_type in MODEL_TYPE_NAME_DICT:
        model_type_name = MODEL_TYPE_NAME_DICT[model_type]
        set_multi_key_value(yaml_data, KEY_PRETRAINED_TYPE, model_type_name[0])
        set_multi_key_value(yaml_data, KEY_PRETRAINED, os.path.join(pretrained_model_path, model_type_name[1]))
    else:
        bcelogger.error('do NOT support model type. {}'.format(model_type))

def generate_train_config(
        advanced_parameters: dict,
        metadata: dict,
        train_config_name: str
):
    """
        modify parameter by template config
    """
    input_yaml_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parameter.yaml')
    yaml_data = get_yaml(input_yaml_name)
    mean, std = [0.5, 0.5, 0.5], [0.5, 0.5, 0.5]
    # 更新metadata
    metadata["algorithmParameters"].update({'mean': mean, 'std': std})

    # 1. set correlative parameters
    correlative_parameter_keys = [KEY_EVAL_WIDTH, KEY_EVAL_HEIGHT, KEY_MODEL_TYPE, KEY_PRETRAINED]
    # 1.1 target size
    set_target_size(yaml_data, advanced_parameters[KEY_EVAL_WIDTH], advanced_parameters[KEY_EVAL_HEIGHT])

    # 1.2 pretrained
    set_pretrained(yaml_data, advanced_parameters[KEY_MODEL_TYPE], advanced_parameters[KEY_PRETRAINED])

    # 2. set get-though parameters by key-value of dict
    for key, val in advanced_parameters.items():
        if key not in correlative_parameter_keys:
            set_multi_key_value(yaml_data, key, val)
            
    bcelogger.info('begin to save yaml. {}'.format(train_config_name))
    save_yaml(yaml_data, train_config_name)
    bcelogger.info('write train config finish.')

def parse_opt():
    """ parser opt
        Args:

        Returns:
            opt -- command line parameter
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--advanced_parameters', type=str, default="", help='train parameter dict')
    parser.add_argument('--train_config_name', type=str, default="", help='output train config file name')
    option = parser.parse_args()
    return option

def str2dict(str):
    """
        demo use only
    """
    s = str.split(',')
    param_dict = {}
    for _, v in enumerate(s):
        kv = v.split(':')
        param_dict[kv[0]] = kv[1]
    return param_dict


if __name__ == "__main__":
    opt = parse_opt()
    from bcelogger.base_logger import setup_logger
    setup_logger(config=dict(file_name=os.path.join("/ssd2/lyg/GAEA-PIPE/ocrnet", "worker.log")))
    meta = {'algorithmParameters': {'evalHeight': 512, 'evalWidth': 512}, 
            'experimentName': None, 'experimentRunID': None, 'extraLoadModel': None, 
            'inputSize': {'height': 512, 'width': 512}, 
            'jobName': None, 'labels': [], 'maxBoxNum': None}
    advanced_parameters = {"iters": "100", "lr_scheduler.learning_rate": "0.001",
                            "eval_height": "512", "eval_width": "512", "batch_size": "6", "model_type": "ocrnet",
                            "model.backbone.pretrained": "/ssd2/lyg/GAEA-PIPE/ocrnet/pretrained_model"}
    opt.train_config_name = '/ssd2/lyg/GAEA-PIPE/ocrnet/train_config.yaml'
    generate_train_config(advanced_parameters=advanced_parameters,
                          metadata=meta, train_config_name=opt.train_config_name)