#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/21
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from paddleflow.pipeline import ContainerStep
from paddleflow.pipeline import Artifact


def package_step(algorithm: str,
                 transform_eval_step: ContainerStep = None,
                 transform_step: ContainerStep = None,
                 windmill_ak: str = "",
                 windmill_sk: str = "",
                 windmill_endpoint: str = "",
                 experiment_kind: str = "",
                 experiment_name: str = "",
                 modelstore_name: str = "",
                 tracking_uri: str = "",
                 project_name: str = "",
                 accelerator: str = "",
                 ensemble_model_name: str = "",
                 ensemble_model_display_name: str = "",
                 sub_model_names: str = "",
                 scene: str = ""):
    """
    Package step
    """
    package_params = {"flavour": "c4m16",
                      "queue": "qtrain",
                      "windmill_ak": windmill_ak,
                      "windmill_sk": windmill_sk,
                      "windmill_endpoint": windmill_endpoint,
                      "experiment_name": experiment_name,
                      "experiment_kind": experiment_kind,
                      "tracking_uri": tracking_uri,
                      "project_name": project_name,
                      "model_store_name": modelstore_name,
                      "accelerator": accelerator,
                      "ensemble_model_name": ensemble_model_name,
                      "ensemble_model_display_name": ensemble_model_display_name,
                      "sub_model_names": sub_model_names,
                      "scene": scene}
    package_env = {"PF_JOB_FLAVOUR": "{{flavour}}",
                   "PF_JOB_QUEUE_NAME": "{{queue}}",
                   "WINDMILL_AK": "{{windmill_ak}}",
                   "WINDMILL_SK": "{{windmill_sk}}",
                   "WINDMILL_ENDPOINT": "{{windmill_endpoint}}",
                   "EXPERIMENT_KIND": "{{experiment_kind}}",
                   "EXPERIMENT_NAME": "{{experiment_name}}",
                   "TRACKING_URI": "{{tracking_uri}}",
                   "PROJECT_NAME": "{{project_name}}",
                   "ACCELERATOR": "{{accelerator}}",
                   "ENSEMBLE_MODEL_NAME": "{{ensemble_model_name}}",
                   "ENSEMBLE_MODEL_DISPLAY_NAME": "{{ensemble_model_display_name}}",
                   "SUB_MODEL_NAMES": "{{sub_model_names}}",
                   "SCENE": "{{scene}}"}

    package = ContainerStep(name="package",
                            docker_env="iregistry.baidu-int.com/windmill-public/inference/"
                                       "triton_r22_12_nvidia_infer_trt86:v1.2.0",
                            env=package_env,
                            parameters=package_params,
                            inputs={"input_model_uri": transform_step.outputs["output_model_uri"]},
                            outputs={"output_model_uri": Artifact(), "output_uri": Artifact()},
                            command=f'python3 -m gaea_operator.components.package.package '
                                    f'--algorithm={algorithm} '
                                    f'--input-model-uri={{{{input_model_uri}}}} '
                                    f'--output-uri={{{{output_uri}}}} '
                                    f'--output-model-uri={{{{output_model_uri}}}}').after(transform_eval_step)

    return package
