#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/17
# @Author  : yanxiaodong
# @File    : metric.py
"""
from typing import Optional, List, Union
from pydantic import BaseModel

LOSS_METRIC_NAME = "Loss"
MAP_METRIC_NAME = "mAP"
AP50_METRIC_NAME = "AP50"
AR_METRIC_NAME = "AR"
MIOU_METRIC_NAME = "mIOU"
ACCURACY_METRIC_NAME = "ACC"
BOUNDING_BOX_LABEL_METRIC_NAME = "boundingBoxLabelMetric"
BOUNDING_BOX_MEAN_AVERAGE_PRECISION_METRIC_NAME = "boundingBoxMeanAveragePrecision"
BOUNDING_BOX_MEAN_AVERAGE_RECALL_METRIC_NAME = "boundingBoxMeanAverageRecall"
BOUNDING_BOX_LABEL_AVERAGE_PRECISION_METRIC_NAME = "boundingBoxLabelAveragePrecision"
CONFUSION_MATRIX_METRIC_NAME = "confusionMatrix"
CLASSIFICATION_ACCURACY_METRIC_NAME = "accuracy"
CLASSIFICATION_LABEL_PRECISION_METRIC_NAME = "LabelPrecision"
SEMANTIC_SEGMENTATION_MIOU_METRIC_NAME = "meanIntersectionOverUnionMetric"
SEMANTIC_SEGMENTATION_LABEL_IOU_METRIC_NAME = "labelIntersectionOverUnionMetric"
LABEL_STATISTIC_METRIC = "labelStatisticMetric"
ANNOTATION_CONFIDENCE_STATISTIC_METRIC = "annotationConfidenceStatisticMetric"
ANNOTATION_AREA_STATISTIC_METRIC = "annotationAreaStatisticMetric"
ANNOTATION_HEIGHT_STATISTIC_METRIC = "annotationHeightStatisticMetric"
ANNOTATION_WIDTH_STATISTIC_METRIC = "annotationWidthStatisticMetric"
INFERENCE_LABEL_METRIC_NAME = "labelMetric"


class Label(BaseModel):
    """
    Labeled Object
    """
    id: int
    name: str


class BaseMetric(BaseModel):
    """
    Metric Object
    """
    artifactName: Optional[str] = None
    datasetName: Optional[str] = None
    annotationSetName: Optional[str] = None
    baselineJobName: Optional[str] = None
    taskKind: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class BaseTrainMetric(BaseModel):
    """
    Loss Metric
    """
    name: Optional[str] = None
    displayName: Optional[str] = None
    result: Optional[float] = None


class TrainMetric(BaseModel):
    """
    Object Detection Metric
    """
    epoch: Optional[str] = None
    step: Optional[str] = None
    metrics: Optional[List[BaseTrainMetric]] = None


class StatisticMetric(BaseModel):
    """
    Confidence Cut
    """
    lowerBound: Optional[float] = None
    upperBound: Optional[float] = None
    bboxCount: Optional[int] = None


class LabelCutStatisticResult(BaseModel):
    """
    Label confidence statistics result
    """
    labelName: Optional[str] = None
    statisticStep: Optional[float] = None
    statisticMetrics: Optional[List[StatisticMetric]] = None


class LabelCutStatistic(BaseModel):
    """
    Label confidence statistics metric
    """
    name: Optional[str] = None
    displayName: Optional[str] = None
    result: Optional[List[LabelCutStatisticResult]] = None


class LabelCountStatisticResult(BaseModel):
    """
    Label count statistics result
    """
    labelName: Optional[str] = None
    labelCount: Optional[int] = None


class LabelCountStatistic(BaseModel):
    """
    Label count statistics metric
    """
    name: Optional[str] = None  # labelStatisticMetric
    displayName: Optional[str] = None
    result: Optional[List[LabelCountStatisticResult]] = None


class LabelStatisticsMetric(BaseMetric):
    """
    Label statistics metric
    """
    labels: Optional[List[Label]] = None
    metrics: Optional[List[Union[
        LabelCountStatistic,
        LabelCutStatistic]]] = None


class InferenceLabelMetricResult(BaseModel):
    """
    Inference label metric result
    """
    labelName: Optional[str] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    accuracy: Optional[float] = None


class InferenceLabelMetric(BaseModel):
    """
    Inference label metric
    """
    name: Optional[str] = None  # labelMetric
    displayName: Optional[str] = None
    result: Optional[List[InferenceLabelMetricResult]] = None


class InferenceMetric(BaseMetric):
    """
    Label statistics metric
    """
    labels: Optional[List[Label]] = None
    metrics: Optional[List[Union[InferenceLabelMetric]]] = None


class ConfusionMatrixAnnotationSpec(BaseModel):
    """
    Confusion Matrix Result
    """
    id: Optional[int] = None
    labelName: Optional[str] = None


class ConfusionMatrixRow(BaseModel):
    """
    Confusion Matrix Result
    """
    row: Optional[List[int]] = None


class ConfusionMatrixMetricResult(BaseModel):
    """
    Confusion Matrix Result
    """
    lowerBound: Optional[int] = None
    upperBound: Optional[int] = None
    annotationSpecs: Optional[List[ConfusionMatrixAnnotationSpec]] = None
    rows: Optional[List[ConfusionMatrixRow]] = None


class ConfusionMatrixMetric(BaseModel):
    """
    Confusion Matrix
    """
    name: Optional[str] = None  # confusionMatrix
    displayName: Optional[str] = None
    result: Optional[ConfusionMatrixMetricResult] = None
