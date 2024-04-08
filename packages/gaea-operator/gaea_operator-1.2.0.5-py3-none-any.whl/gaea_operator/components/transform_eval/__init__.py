#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/21
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from paddleflow.pipeline import ContainerStep
from paddleflow.pipeline import Artifact

from gaea_operator.utils import get_accelerator


def transform_eval_step(algorithm: str,
                        eval_step: ContainerStep = None,
                        transform_step: ContainerStep = None,
                        windmill_ak: str = "",
                        windmill_sk: str = "",
                        windmill_endpoint: str = "",
                        experiment_kind: str = "",
                        experiment_name: str = "",
                        modelstore_name: str = "",
                        tracking_uri: str = "",
                        project_name: str = "",
                        accelerator: str = ""):
    """
    Transform eval step
    """
    transform_eval_params = {"flavour": "c4m16gpu1",
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
                             "advanced_parameters": '{"conf_threshold":"0.1",'
                                                    '"iou_threshold":"0.50"}'}
    transform_eval_env = {"PF_JOB_FLAVOUR": "{{flavour}}",
                          "PF_JOB_QUEUE_NAME": "{{queue}}",
                          "WINDMILL_AK": "{{windmill_ak}}",
                          "WINDMILL_SK": "{{windmill_sk}}",
                          "WINDMILL_ENDPOINT": "{{windmill_endpoint}}",
                          "EXPERIMENT_KIND": "{{experiment_kind}}",
                          "EXPERIMENT_NAME": "{{experiment_name}}",
                          "TRACKING_URI": "{{tracking_uri}}",
                          "PROJECT_NAME": "{{project_name}}",
                          "ACCELERATOR": "{{accelerator}}",
                          "ADVANCED_PARAMETERS": "{{advanced_parameters}}"}
    accelerator = get_accelerator(name=accelerator)
    transform_eval_env.update(accelerator.suggest_env())

    transform_eval = ContainerStep(name="transform-eval",
                                   docker_env=accelerator.suggest_image(),
                                   env=transform_eval_env,
                                   parameters=transform_eval_params,
                                   inputs={"input_dataset_uri": eval_step.outputs["output_dataset_uri"],
                                           "input_model_uri": transform_step.outputs["output_model_uri"]},
                                   outputs={"output_uri": Artifact()},
                                   command=f'python3 -m gaea_operator.components.transform_eval.transform_eval '
                                           f'--algorithm={algorithm} '
                                           f'--input-model-uri={{{{input_model_uri}}}} '
                                           f'--input-dataset-uri={{{{input_dataset_uri}}}} '
                                           f'--output-uri={{{{output_uri}}}}')


    return transform_eval
