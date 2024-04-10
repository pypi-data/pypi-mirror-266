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


def inference_step(eval_step: ContainerStep = None,
                   package_step: ContainerStep = None,
                   windmill_ak: str = "",
                   windmill_sk: str = "",
                   windmill_endpoint: str = "",
                   experiment_kind: str = "",
                   experiment_name: str = "",
                   model_store_name: str = "",
                   tracking_uri: str = "",
                   project_name: str = "",
                   accelerator: str = ""):
    """
    Inference step
    """
    inference_params = {"flavour": "c4m16gpu1",
                        "queue": "qtrain",
                        "windmill_ak": windmill_ak,
                        "windmill_sk": windmill_sk,
                        "windmill_endpoint": windmill_endpoint,
                        "experiment_name": experiment_name,
                        "experiment_kind": experiment_kind,
                        "tracking_uri": tracking_uri,
                        "project_name": project_name,
                        "model_store_name": model_store_name,
                        "accelerator": accelerator}
    inference_env = {"PF_JOB_FLAVOUR": "{{flavour}}",
                     "PF_JOB_QUEUE_NAME": "{{queue}}",
                     "WINDMILL_AK": "{{windmill_ak}}",
                     "WINDMILL_SK": "{{windmill_sk}}",
                     "WINDMILL_ENDPOINT": "{{windmill_endpoint}}",
                     "EXPERIMENT_KIND": "{{experiment_kind}}",
                     "EXPERIMENT_NAME": "{{experiment_name}}",
                     "TRACKING_URI": "{{tracking_uri}}",
                     "PROJECT_NAME": "{{project_name}}",
                     "ACCELERATOR": "{{accelerator}}"}
    accelerator = get_accelerator(name=accelerator)
    inference_env.update(accelerator.suggest_env())

    inference = ContainerStep(name="inference",
                              docker_env=accelerator.suggest_image(),
                              env=inference_env,
                              parameters=inference_params,
                              inputs={"input_dataset_uri": eval_step.outputs["output_dataset_uri"],
                                      "input_model_uri": package_step.outputs["output_model_uri"]},
                              outputs={"output_uri": Artifact()},
                              command=f'python3 -m gaea_operator.components.inference.inference '
                                      f'--input-model-uri={{{{input_model_uri}}}} '
                                      f'--input-dataset-uri={{{{input_dataset_uri}}}} '
                                      f'--output-uri={{{{output_uri}}}}')

    return inference
