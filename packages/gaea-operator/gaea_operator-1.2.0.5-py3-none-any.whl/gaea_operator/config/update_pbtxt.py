# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Baidu.com, Inc. All Rights Reserved
#
"""
config.pbtxt配置文件更新
Authors: wanggaofei(wanggaofei03@baidu.com)
Date:    2023-03-16
"""
#!/usr/bin/env python3


import json
import os
from copy import deepcopy
from shutil import copytree
from typing import Any, Dict, List, Optional

from google.protobuf import json_format, text_format
from google.protobuf.descriptor import FieldDescriptor
from tritonclient.grpc import model_config_pb2
import bcelogger

KEY_DIMS = 'dims'
KEY_OUTPUT = 'output'
KEY_OPTIMIZATION = 'optimization'
KEY_EXECUTION_ACCELERATORS = 'executionAccelerators'
KEY_CPU_EXECUTION_ACCELERATOR = 'cpuExecutionAccelerator'
KEY_TYPE = 'type'
KEY_NAME = 'name'
KEY_WIDTH = 'width'
KEY_HEIGHT = 'height'
KEY_ENSEMBLE_SCHEDULING = 'ensembleScheduling'
KEY_STEP = 'step'
KEY_MODEL_NAME = 'modelName'
KEY_MODEL_VERSION = 'modelVersion'
KEY_PARAMETERS = 'parameters'

class ModelConfig:
    """
    A class that encapsulates all the metadata about a Triton model.
    """

    _default_config_dict: Dict[str, Any] = {}

    def __init__(self, model_config):
        """
        Parameters
        -------
        model_config : protobuf message
        """

        self._model_config = model_config

    def to_dict(self):
        """
            将模型配置转换为字典格式，返回值类型是dict。
        该方法主要用于将模型配置信息序列化成字典格式，以便进行JSON序列化或其他操作。
        
        Args:
            无参数。
        
        Returns:
            dict (dict): 包含模型配置信息的字典，键值对形如{"key": value}。value可以是任意类型，包括int、float、str等。
        """
        model_config_dict = json_format.MessageToDict(self._model_config)
        return model_config_dict

    @classmethod
    def from_dict(cls, model_config_dict):
        """
            从字典中创建模型配置。
        参数:
            model_config_dict (dict): 包含模型配置信息的字典，必须包含以下键值对：
                - "model_name" (str): 模型名称。
                - "pretrained" (bool, optional): 是否使用预训练权重（默认为False）。
                - "weights" (str, optional): 预训练权重文件路径（如果不存在则使用预训练权重）。
                - "num_classes" (int, optional): 类别数量（默认为80）。
                - "backbone" (str, optional): 后端网络名称（默认为'resnet50'）。
                - "input_size" (int, optional): 输入图像大小（默认为224）。
                - "pooling" (str, optional): 池化方式（默认为'avg'）。
                - "interpolation" (str, optional): 插值方式（默认为'bicubic'）。
                - "mean" (list[float], optional): 归一化均值（默认为[0.485, 0.456, 0.406]）。
                - "std" (list[float], optional): 归一化标准差（默认为[0.229, 0.224, 0.225]）。
                - "device" (str, optional): 设备名称（默认为'cuda'）。
        返回值:
            ModelConfig (object): 模型配置实例。
        """
        return ModelConfig.create_from_dictionary(model_config_dict)

    
    @staticmethod
    def _create_from_file(pbtxt_name):
        """
        Constructs a ModelConfig from the pbtxt at file

        Parameters
        -------
        pbtxt_name : str
            The full path to config.pbtxt

        Returns
        -------
        ModelConfig
        """
        if not os.path.isfile(pbtxt_name):
            bcelogger.error(
                f'Path "{pbtxt_name}" does not exist.'
                " Make sure that you have specified the correct model"
                " repository and model name(s)."
            )

        with open(pbtxt_name, "r+") as f:
            config_str = f.read()

        protobuf_message = text_format.Parse(config_str, model_config_pb2.ModelConfig())

        return ModelConfig(protobuf_message)

    @staticmethod
    def create_from_dictionary(model_dict):
        """
        Constructs a ModelConfig from a Python dictionary

        Parameters
        -------
        model_dict : dict
            A dictionary containing the model configuration.

        Returns
        -------
        ModelConfig
        """

        protobuf_message = json_format.ParseDict(
            model_dict, model_config_pb2.ModelConfig()
        )

        return ModelConfig(protobuf_message)

    def is_ensemble(self) -> bool:
        """
        Returns
        -------
        bool
           True if this is an ensemble model
        """

        return getattr(self._model_config, "platform") == "ensemble"

    def get_ensemble_composing_models(self) -> Optional[List[str]]:
        """
        Returns
        -------
            List[str]: Sub-model names
        """

        if not self.is_ensemble():
            bcelogger.error(
                "Cannot find composing_models. Model platform is not ensemble."
            )

        try:
            composing_models = [
                model["modelName"]
                for model in self.to_dict()["ensembleScheduling"]["step"]
            ]
        except Exception:
            bcelogger.error(
                "Cannot find composing_models. Ensemble Scheduling and/or step is not present in config protobuf."
            )

        return composing_models

    def set_composing_model_variant_name(
        self, composing_model_name: str, variant_name: str
    ) -> None:
        """
        Replaces the Ensembles composing_model's name with the variant name
        """

        if not self.is_ensemble():
            bcelogger.error(
                "Cannot find composing_models. Model platform is not ensemble."
            )

        model_config_dict = self.to_dict()

        try:
            for composing_model in model_config_dict["ensembleScheduling"]["step"]:
                if composing_model["modelName"] == composing_model_name:
                    composing_model["modelName"] = variant_name
        except Exception:
            bcelogger.error(
                "Cannot find composing_models. Ensemble Scheduling and/or step is not present in config protobuf."
            )

        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_model_name(self, model_name: str) -> None:
        """
            设置模型名称。
        
        Args:
            model_name (str): 模型名称，字符串类型。
        
        Returns:
            None: 无返回值，直接修改了当前对象的模型名称。
        """
        model_config_dict = self.to_dict()
        model_config_dict["name"] = model_name
        self._model_config = self.from_dict(model_config_dict)._model_config

    def write_config_to_file(
        self, pbtxt_name
    ):
        """
        Writes a protobuf config file.

        Parameters
        ----------
        pbtxt_name : str
            config.pbtxt file to be saved

        Raises
        ------
        TritonModelAnalyzerException
            If the path doesn't exist or the path is a file
        """

        model_config_bytes = text_format.MessageToBytes(self._model_config)
        # Create current variant model as symlinks to first variant model

        with open(pbtxt_name, "wb") as f:
            f.write(model_config_bytes)

    def get_config(self):
        """
        Get the model config.

        Returns
        -------
        dict
            A dictionary containing the model configuration.
        """

        return json_format.MessageToDict(
            self._model_config, preserving_proto_field_name=True
        )

    def get_config_str(self):
        """
        Get the model config json str

        Returns
        -------
        str
            A JSON string containing the model configuration.
        """
        return json.dumps(self.get_config())

    def set_config(self, config):
        """
        Set the model config from a dictionary.

        Parameters
        ----------
        config : dict
            The new dictionary containing the model config.
        """

        self._model_config = json_format.ParseDict(
            config, model_config_pb2.ModelConfig()
        )

    def set_field(self, name, value):
        """
        Set a value for a Model Config field.

        Parameters
        ----------
        name : str
            Name of the field
        value : object
            The value to be used for the field.
        """
        model_config = self._model_config

        if (
            model_config.DESCRIPTOR.fields_by_name[name].label
            == FieldDescriptor.LABEL_REPEATED
        ):
            repeated_field = getattr(model_config, name)
            del repeated_field[:]
            repeated_field.extend(value)
        else:
            setattr(model_config, name, value)

    def set_output_dims(self, idx, dims):
        """
            set output node dims
        """
        model_config_dict = self.to_dict()
        if KEY_OUTPUT in model_config_dict:
            for v in model_config_dict[KEY_OUTPUT]:
                if KEY_DIMS in v and idx + len(dims) <= len(v[KEY_DIMS]):
                    self.set_dict_dims(v, idx, dims)
        self._model_config = self.from_dict(model_config_dict)._model_config
    
    def set_dict_dims(self, config_dict, idx: int, dims: list):
        """
            set array dims
        """
        if KEY_DIMS not in config_dict or len(dims) + idx > len(config_dict[KEY_DIMS]):
            bcelogger.error('do NOT find dims in config or dims invalid. idx: {} dims: {}'.format(idx, dims))
        else:
            config_dict[KEY_DIMS][idx: idx + len(dims)] = dims

    def set_op_resize_width_height(self, width: int, height: int):
        """
            set all resize-type op width/height
        """
        model_config_dict = self.to_dict()
        if KEY_OPTIMIZATION in model_config_dict and \
            KEY_EXECUTION_ACCELERATORS in model_config_dict[KEY_OPTIMIZATION] and \
            KEY_CPU_EXECUTION_ACCELERATOR in model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS]:
            cpu_exec_acc_dag = \
                model_config_dict[KEY_OPTIMIZATION][KEY_EXECUTION_ACCELERATORS][KEY_CPU_EXECUTION_ACCELERATOR]
            for v in cpu_exec_acc_dag:
                if KEY_PARAMETERS in v and KEY_TYPE in v[KEY_PARAMETERS] and KEY_WIDTH in v[KEY_PARAMETERS] and \
                    KEY_HEIGHT in v[KEY_PARAMETERS] and v[KEY_PARAMETERS][KEY_TYPE] == 'resize':
                    v[KEY_PARAMETERS][KEY_WIDTH] = str(width)
                    v[KEY_PARAMETERS][KEY_HEIGHT] = str(height)
        self._model_config = self.from_dict(model_config_dict)._model_config

    def set_preproc_width_height(self, idx: int, width: int, height: int, is_nhwc: bool):
        """
            set preprocess width/height parameter
        """
        # 1. set output
        if is_nhwc:
            dims = [height, width]
        else:
            dims = [width, height]
        self.set_output_dims(idx, dims)

        # 2. set resize op
        self.set_op_resize_width_height(width, height)

    def set_ppyoloe_output_max_box_count(self, val: int):
        """
        modify ppyoloe output max-box-count config (nvidia/kunlun)
        """
        output_names = ['det_boxes', 'det_scores', 'det_classes']
        model_config_dict = self.to_dict()
        if KEY_OUTPUT in model_config_dict:
            for v in model_config_dict[KEY_OUTPUT]:
                if KEY_NAME in v and v[KEY_NAME] in output_names and KEY_DIMS in v:
                    self.set_dict_dims(v, 0, [val])
        self._model_config = self.from_dict(model_config_dict)._model_config
        
    def set_ensemble_step_model_name_and_version(self, names: dict, versions: dict):
        """
            modify ensemel step model names
        """
        model_config_dict = self.to_dict()
        if KEY_ENSEMBLE_SCHEDULING in model_config_dict and KEY_STEP in model_config_dict[KEY_ENSEMBLE_SCHEDULING]:
            for v in model_config_dict[KEY_ENSEMBLE_SCHEDULING][KEY_STEP]:
                if KEY_MODEL_NAME in v and v[KEY_MODEL_NAME] in names:
                    v[KEY_MODEL_VERSION] = versions[v[KEY_MODEL_NAME]]
                    v[KEY_MODEL_NAME] = names[v[KEY_MODEL_NAME]]
                    bcelogger.info('modify model name: {}'.format(v[KEY_MODEL_NAME]))
        self._model_config = self.from_dict(model_config_dict)._model_config

    def get_field(self, name):
        """
        Get the value for the current field.
        """

        model_config = self._model_config
        return getattr(model_config, name)

    def max_batch_size(self) -> int:
        """
        Returns the max batch size (int)
        """

        model_config = self.get_config()
        return model_config.get("max_batch_size", 0)

    def dynamic_batching_string(self) -> str:
        """
        Returns
        -------
        str
            representation of the dynamic batcher
            configuration used to generate this result
        """

        model_config = self.get_config()
        if "dynamic_batching" in model_config:
            return "Enabled"
        else:
            return "Disabled"

    def instance_group_count(self, system_gpu_count: int) -> int:
        """
        Returns:
            int: The total number of instance groups (cpu + gpu)
        """

        kind_to_count = self._get_instance_groups(system_gpu_count)
        instance_group_count = sum([count for count in kind_to_count.values()])

        return instance_group_count

    def instance_group_string(self, system_gpu_count: int) -> str:
        """
        Returns
        -------
        str
            representation of the instance group used
            to generate this result

            Format is "GPU:<count> + CPU:<count>"
        """

        kind_to_count = self._get_instance_groups(system_gpu_count)

        ret_str = ""
        for k, v in kind_to_count.items():
            if ret_str != "":
                ret_str += " + "
            ret_str += f"{v}:{k}"
        return ret_str

    def _get_instance_groups(self, system_gpu_count: int) -> Dict[str, int]:
        """
        Returns a dictionary with type of instance (GPU/CPU) and its count
        """
        model_config = self.get_config()

        # TODO change when remote mode is fixed
        default_kind = "CPU"
        default_count = 1

        instance_group_list: List[Dict[str, Any]] = [{}]
        if "instance_group" in model_config:
            instance_group_list = model_config["instance_group"]

        kind_to_count: Dict[str, Any] = {}

        for group in instance_group_list:
            group_kind = default_kind
            group_count = default_count
            group_gpus_count = system_gpu_count
            # Update with instance group values
            if "kind" in group:
                group_kind = group["kind"].split("_")[1]
            if "count" in group:
                group_count = group["count"]
            if "gpus" in group:
                group_gpus_count = len(group["gpus"])

            group_total_count = group_count
            if group_kind == "GPU":
                group_total_count *= group_gpus_count

            if group_kind not in kind_to_count:
                kind_to_count[group_kind] = 0
            kind_to_count[group_kind] += group_total_count

        return kind_to_count

if __name__ == "__main__":
    # 1. ensemble
    pbtxt_path = './ensemble.pbtxt'
    pbtxt = ModelConfig._create_from_file(pbtxt_path)
    print('is ensemble: {}'.format(pbtxt.is_ensemble()))
    pbtxt.set_field('max_batch_size', 100)
    
    names = {
        'ppyoloeplus-preprocess': 'abc-preprocess',
        'ppyoloeplus-model': 'abc-model',
        'ppyoloeplus-postprocess': 'abc-postprocess',
    }

    pbtxt.set_ensemble_step_model_name(names)
    dst_path = './output_ensemble.pbtxt'
    pbtxt.write_config_to_file(dst_path)

    # 2. preproc
    pbtxt_path = './preproc.pbtxt'
    pbtxt = ModelConfig._create_from_file(pbtxt_path)
    pbtxt.set_field('max_batch_size', 100)

    pbtxt.set_preproc_width_height(idx=0, width=1920, height=1080, is_nhwc=True)
    dst_path = './output_preproc.pbtxt'
    pbtxt.write_config_to_file(dst_path)

    # 3. model
    pbtxt_path = './model.pbtxt'
    pbtxt = ModelConfig._create_from_file(pbtxt_path)
    pbtxt.set_field('max_batch_size', 100)

    max_box_count = 100
    pbtxt.set_ppyoloe_output_max_box_count(max_box_count)
    dst_path = './output_model.pbtxt'
    pbtxt.write_config_to_file(dst_path)
