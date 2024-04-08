#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/23
# @Author  : yanxiaodong
# @File    : transform_component.py
"""
import json
import os
from argparse import ArgumentParser

from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
import bcelogger
from windmillmodelv1.client.model_api_model import parse_model_name
from windmillartifactv1.client.artifact_api_artifact import get_name
from windmillclient.client.windmill_client import WindmillClient

from gaea_operator.config import Config
from gaea_operator.model import format_name
from gaea_operator.utils import read_file, \
    write_file, \
    find_dir, \
    get_accelerator, \
    get_model_template


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--windmill-ak", type=str, default=os.environ.get("WINDMILL_AK"))
    parser.add_argument("--windmill-sk", type=str, default=os.environ.get("WINDMILL_SK"))
    parser.add_argument("--windmill-endpoint", type=str, default=os.environ.get("WINDMILL_ENDPOINT"))
    parser.add_argument("--project-name", type=str, default=os.environ.get("PROJECT_NAME"))
    parser.add_argument("--public-model-store",
                        type=str,
                        default=os.environ.get("PUBLIC_MODEL_STORE", "workspaces/public/modelstores/public"))
    parser.add_argument("--tracking-uri", type=str, default=os.environ.get("TRACKING_URI"))
    parser.add_argument("--experiment-name", type=str, default=os.environ.get("EXPERIMENT_NAME"))
    parser.add_argument("--experiment-kind", type=str, default=os.environ.get("EXPERIMENT_KIND"))
    parser.add_argument("--ensemble-model-name",
                        type=str,
                        default=os.environ.get("ENSEMBLE_MODEL_NAME"))
    parser.add_argument("--ensemble-model-display-name",
                        type=str,
                        default=os.environ.get("ENSEMBLE_MODEL_DISPLAY_NAME"))
    parser.add_argument("--accelerator", type=str, default=os.environ.get("ACCELERATOR", "t4"))
    parser.add_argument("--algorithm", type=str, default=os.environ.get("ALGORITHM", ""))
    parser.add_argument("--scene", type=str, default=os.environ.get("SCENE", ""))

    parser.add_argument("--input-model-uri", type=str, default=os.environ.get("INPUT_MODEL_URI"))
    parser.add_argument("--output-model-uri", type=str, default=os.environ.get("OUTPUT_MODEL_URI"))
    parser.add_argument("--output-uri", type=str, default=os.environ.get("OUTPUT_URI"))

    args, _ = parser.parse_known_args()

    return args


def package(args):
    """
    Package component for ppyoloe_plus model.
    """
    windmill_client = WindmillClient(ak=args.windmill_ak,
                                     sk=args.windmill_sk,
                                     endpoint=args.windmill_endpoint)
    tracker_client = ExperimentTracker(windmill_client=windmill_client,
                                       tracking_uri=args.tracking_uri,
                                       experiment_name=args.experiment_name,
                                       experiment_kind=args.experiment_kind,
                                       project_name=args.project_name)
    setup_logger(config=dict(file_name=os.path.join(args.output_uri, "worker.log")))

    response = read_file(input_dir=args.input_model_uri)
    metadata = response["artifact"]["metadata"]

    model_template = get_model_template(name=args.algorithm, model_store_name=args.public_model_store)
    ppyoloe_plus_model_to_res = {parse_model_name(model_template.suggest_template_model()).local_name: response}

    # 1. 下载ensemble template 模型
    ensemble_artifact_name = get_name(object_name=model_template.suggest_template_ensemble(), version="latest")
    bcelogger.info(f"Dumping model {ensemble_artifact_name} to {args.output_model_uri}")
    windmill_client.dump_models(artifact_name=ensemble_artifact_name,
                                location_style="Triton",
                                rename="ensemble",
                                output_uri=args.output_model_uri)

    # 2. 生成打包配置文件
    modify_model_names = {
        'preprocess': [parse_model_name(model_template.suggest_template_preprocess()).local_name],
        'postprocess': [parse_model_name(model_template.suggest_template_postprocess()).local_name],
        'ensemble': [parse_model_name(model_template.suggest_template_ensemble()).local_name]
    }

    model_name = parse_model_name(name=args.ensemble_model_name)
    workspace_id = model_name.workspace_id
    model_store_name = model_name.model_store_name
    ensemble_local_name = model_name.local_name

    config = Config(windmill_client=windmill_client, tracker_client=tracker_client, metadata=metadata)
    config.write_triton_package_config(transform_model_uri=args.input_model_uri,
                                       ensemble_model_uri=args.output_model_uri,
                                       modify_model_names=modify_model_names,
                                       ensemble_local_name=ensemble_local_name)

    transform_local_name = response["localName"]
    transform_model_display_name = response["displayName"]
    # 3. 上传 Preprocess 模型
    pre_model_uri = os.path.join(args.output_model_uri,
                                 parse_model_name(model_template.suggest_template_preprocess()).local_name)
    local_name = format_name(transform_local_name, "pre")
    display_name = format_name(transform_model_display_name, "预处理")
    response = windmill_client.create_model(workspace_id=workspace_id,
                                            model_store_name=model_store_name,
                                            local_name=local_name,
                                            display_name=display_name,
                                            category="Image/Preprocess",
                                            model_formats=["Python"],
                                            artifact_uri=find_dir(pre_model_uri))
    bcelogger.info(f"Model {local_name} created response: {response}")
    ppyoloe_plus_model_to_res.update(
        {parse_model_name(model_template.suggest_template_preprocess()).local_name: json.loads(response.raw_data)})

    # 4. 上传 PostProcess 模型
    post_model_uri = os.path.join(args.output_model_uri,
                                  parse_model_name(model_template.suggest_template_postprocess()).local_name)
    local_name = format_name(transform_local_name, "post")
    display_name = format_name(transform_model_display_name, "后处理")
    response = windmill_client.create_model(workspace_id=workspace_id,
                                            model_store_name=model_store_name,
                                            local_name=local_name,
                                            display_name=display_name,
                                            category="Image/Postprocess",
                                            model_formats=["Python"],
                                            artifact_uri=find_dir(post_model_uri))
    bcelogger.info(f"Model {local_name} created response: {response}")
    ppyoloe_plus_model_to_res.update({
        parse_model_name(model_template.suggest_template_postprocess()).local_name: json.loads(response.raw_data)})

    # 5. 修改 ensemble 配置文件
    ensemble_model_uri = os.path.join(args.output_model_uri, "ensemble")
    config.write_ensemble_config(ensemble_model_uri=ensemble_model_uri, model_config=ppyoloe_plus_model_to_res)

    # 6. 上传 ensemble 模型
    accelerator = get_accelerator(name=args.accelerator)
    response = windmill_client.create_model(
        workspace_id=workspace_id,
        model_store_name=model_store_name,
        local_name=ensemble_local_name,
        display_name=args.ensemble_model_display_name,
        prefer_model_server_parameters=accelerator.suggest_model_server_parameters(),
        category="Image/Ensemble",
        model_formats=["Python"],
        artifact_uri=find_dir(ensemble_model_uri))
    bcelogger.info(f"Model {ensemble_local_name} created response: {response}")

    # 4. 输出文件
    write_file(obj=json.loads(response.raw_data), output_dir=args.output_model_uri)


if __name__ == "__main__":
    args = parse_args()
    package(args=args)
