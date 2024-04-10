#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/23
# @Author  : yanxiaodong
# @File    : classify.py
"""
import os
import json
from argparse import ArgumentParser

from gaea_tracker import ExperimentTracker
from bcelogger.base_logger import setup_logger
from windmillmodelv1.client.model_api_model import parse_model_name
from windmillmodelv1.client.model_api_model import ModelName
from windmillmodelv1.client.model_api_modelstore import parse_modelstore_name
from windmillclient.client.windmill_client import WindmillClient
import bcelogger

from gaea_operator.dataset import ImageNetDataset
from gaea_operator.config import ResNetConfig
from gaea_operator.metric.types.metric import LOSS_METRIC_NAME, \
    ACCURACY_METRIC_NAME, \
    CLASSIFICATION_ACCURACY_METRIC_NAME
from gaea_operator.trainer import Trainer
from gaea_operator.model import Model
from gaea_operator.metric import get_score_from_file
from gaea_operator.utils import write_file


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
    parser.add_argument("--train-dataset-name", type=str, default=os.environ.get("TRAIN_DATASET_NAME"))
    parser.add_argument("--val-dataset-name", type=str, default=os.environ.get("VAL_DATASET_NAME"))
    parser.add_argument("--model-name", type=str, default=os.environ.get("MODEL_NAME"))
    parser.add_argument("--model-display-name", type=str, default=os.environ.get("MODEL_DISPLAY_NAME"))
    parser.add_argument("--advanced-parameters", type=str, default=os.environ.get("ADVANCED_PARAMETERS", "{}"))

    parser.add_argument("--output-model-uri", type=str, default=os.environ.get("OUTPUT_MODEL_URI"))
    parser.add_argument("--output-uri", type=str, default=os.environ.get("OUTPUT_URI"))

    args, _ = parser.parse_known_args()

    return args


def resnet_train(args):
    """
    Train component for classify model.
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

    dataset_uri = "/home/windmill/tmp/dataset"
    classify_dataset = ImageNetDataset(windmill_client=windmill_client, work_dir=tracker_client.work_dir)
    # 1. 合并train分片数据集
    classify_dataset.concat_dataset(dataset_name=args.train_dataset_name,
                                    output_dir=dataset_uri,
                                    usage=ImageNetDataset.usages[0])

    # 2. 合并val分片数据集
    classify_dataset.concat_dataset(dataset_name=args.val_dataset_name,
                                    output_dir=dataset_uri,
                                    usage=ImageNetDataset.usages[1])

    # 3. 下载预训练模型
    pretrain_name = ModelName(workspace_id=parse_modelstore_name(args.public_model_store).workspace_id,
                              model_store_name=parse_modelstore_name(args.public_model_store).local_name,
                              local_name="ResNet18_pretrained").get_name()
    pretrain_model_uri = "/home/windmill/tmp/pretrain"
    windmill_client.download_artifact(object_name=pretrain_name, version="latest", output_uri=pretrain_model_uri)

    # 4. 生成训练配置文件，固定名字 train_config.yaml，保存在 model_uri
    config = ResNetConfig(windmill_client=windmill_client, tracker_client=tracker_client)
    config.write_train_config(
        dataset_uri=dataset_uri,
        model_uri=args.output_model_uri,
        advanced_parameters=json.loads(args.advanced_parameters),
        pretrain_model_uri=pretrain_model_uri)

    # 5. 训练
    trainer = Trainer(framework="PaddlePaddle", tracker_client=tracker_client)
    metric_names = [LOSS_METRIC_NAME, ACCURACY_METRIC_NAME]
    trainer.track_model_score(metric_names=metric_names)
    trainer.launch()
    trainer.paddleclas_export(model_dir=args.output_model_uri)

    # 6. 创建模型
    metric_name = CLASSIFICATION_ACCURACY_METRIC_NAME
    current_score = get_score_from_file(filepath=os.path.join(args.output_model_uri, "metric.json"),
                                        metric_name=metric_name)
    best_score, version = Model(windmill_client=windmill_client).get_best_model_score(
        model_name=args.model_name, metric_name=metric_name)
    tags = {metric_name: str(current_score)}
    alias = None
    if current_score >= best_score and version is not None:
        alias = ["best"]
        bcelogger.info(
            f"{metric_name.capitalize()} current score {current_score} >= {best_score}, update [best]")
        tags.update(
            {f"bestReason": f"current.score({current_score}) greater than {version}.score({best_score})"})
    if version is None:
        alias = ["best"]
        bcelogger.info(f"First alias [best] score: {current_score}")
        tags.update({f"bestReason": "current.score({current_score})"})

    model_name = parse_model_name(args.model_name)
    workspace_id = model_name.workspace_id
    model_store_name = model_name.model_store_name
    local_name = model_name.local_name
    response = windmill_client.create_model(workspace_id=workspace_id,
                                            model_store_name=model_store_name,
                                            local_name=local_name,
                                            display_name=args.model_display_name,
                                            category="Image/ImageClassification/MultiClass",
                                            model_formats=["PaddlePaddle"],
                                            artifact_alias=alias,
                                            artifact_tags=tags,
                                            artifact_metadata=config.metadata,
                                            artifact_uri=args.output_model_uri)

    bcelogger.info(f"Model {args.model_name} created response: {response}")

    # 7. 输出文件
    write_file(obj=json.loads(response.raw_data), output_dir=args.output_model_uri)


if __name__ == "__main__":
    args = parse_args()
    resnet_train(args=args)
