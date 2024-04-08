#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/24
# @Author  : yanxiaodong
# @File    : inference.py
"""
import copy
from typing import List, Dict
import numpy as np
import os

from gaea_operator.utils import write_file
from gaea_operator.metric.operator import PrecisionRecallF1score, Accuracy
from gaea_operator.metric.types.metric import InferenceMetric, \
    InferenceLabelMetric, \
    INFERENCE_LABEL_METRIC_NAME, \
    InferenceLabelMetricResult


class InferenceMetricAnalysis(object):
    """
    Inference metric analysis.
    """

    def __init__(self, labels: List = None, images: List[Dict] = None):
        self.labels = labels
        self.images = images
        self.image_dict = {}
        self.img_id_str2int = {}
        self.label_id2index = {}
        self.label_name2id = {}
        self.metric = {}
        self.set_images(images)
        self.set_labels(labels)

    def reset(self):
        """
        Reset metric.
        """
        for _, metric_list in self.metric.items():
            for metric in metric_list:
                metric.reset()

    def set_images(self, images: List[Dict]):
        """
        Set images.
        """
        if images is None:
            return
        self.image_dict = {item["image_id"]: item for item in images}
        self.img_id_str2int = {key: idx + 1 for idx, key in enumerate(self.image_dict)}

    def set_labels(self, labels: List):
        """
        Set labels.
        """
        if labels is None:
            return
        self.labels = [{"id": int(label["id"]), "name": label["name"]} for label in labels]
        self.label_id2index = {label["id"]: idx for idx, label in enumerate(self.labels)}
        self.label_name2id = {label["name"]: label["id"] for label in self.labels}
        self.set_metric()

    def set_metric(self):
        """
        Set metric.
        """
        _metric = [Accuracy(num_classes=2), PrecisionRecallF1score(num_classes=2)]
        self.metric = {label["name"]: copy.deepcopy(_metric) for label in self.labels}

    def update(self, predictions: List[Dict], references: List[Dict]):
        """
        Update metric.
        """
        predictions, references = self._format_input(predictions, references)

        for name, metric_list in self.metric.items():
            for metric in metric_list:
                index = self.label_id2index[self.label_name2id[name]]
                metric.update(predictions=predictions[:, index], references=references[:, index])

    def _format_input(self, predictions: List[Dict], references: List[Dict]):
        """
        Format to object detection metric.
        """
        predictions_list = []
        for item in predictions:
            array_item = np.zeros(len(self.labels), dtype=np.int8)
            for anno in item["annotations"]:
                for idx in range(len(anno["labels"])):
                    label_id = int(anno["labels"][idx]["id"])
                    index = self.label_id2index[label_id]
                    array_item[index] = 1
            predictions_list.append(array_item)

        references_list = []
        for item in references:
            array_item = np.zeros(len(self.labels), dtype=np.int8)
            for anno in item["annotations"]:
                for idx in range(len(anno["labels"])):
                    if isinstance(anno["labels"][idx]["id"], int) or isinstance(anno["labels"][idx]["id"], str):
                        label_id = int(anno["labels"][idx]["id"])
                        index = self.label_id2index[label_id]
                        array_item[index] = 1
            references_list.append(array_item)

        return np.array(predictions_list), np.array(references_list)

    def _format_result(self, metric_result: Dict):
        metric = InferenceMetric(labels=self.labels, metrics=[])
        label_metric = InferenceLabelMetric(name=INFERENCE_LABEL_METRIC_NAME,
                                            displayName="类别指标",
                                            result=[])
        for name, result in metric_result.items():
            accuracy = result[self.metric[name][0].global_name()]
            precision = result[self.metric[name][1].global_name()][0]
            recall = result[self.metric[name][1].global_name()][1]

            inference_label_metric_result = InferenceLabelMetricResult(labelName=name,
                                                                       precision=precision,
                                                                       recall=recall,
                                                                       accuracy=accuracy)
            label_metric.result.append(inference_label_metric_result)

        metric.metrics.extend([label_metric])
        return metric.dict()

    def compute(self):
        """
        Compute metric.
        """
        results = {}
        for name, metric_list in self.metric.items():
            results[name] = {}
            for metric in metric_list:
                results[name][metric.name] = metric.compute()

        metric_result = self._format_result(metric_result=results)

        return metric_result

    def save(self, metric_result: Dict, output_uri: str):
        """
        Save metric.
        """
        if os.path.splitext(output_uri)[1] == "":
            output_dir = output_uri
            file_name = "metric.json"
        else:
            output_dir = os.path.dirname(output_uri)
            file_name = os.path.basename(output_uri)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        write_file(obj=metric_result, output_dir=output_dir, file_name=file_name)

    def __call__(self, predictions: List[Dict], references: List[Dict], output_uri: str):
        self.update(predictions=predictions, references=references)
        metric_result = self.compute()

        self.save(metric_result=metric_result, output_uri=output_uri)
