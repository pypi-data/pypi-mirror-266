#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File          : confusion_matrix.py    
@Author        : yanxiaodong
@Date          : 2023/5/25
@Description   :
"""
from typing import List, Dict, Any
from collections import defaultdict
import copy

import numpy as np
from pycocotools import mask as mask_utils

from gaea_operator.utils import Tensor
from ..metric import MetricOperator
from gaea_operator.utils import METRIC


@METRIC.register_module('bbox_confusion_matrix')
class BboxConfusionMatrix(MetricOperator):
    """
    Confusion matrix of the evaluation.
    """
    metric_name = 'bbox_confusion_matrix'

    def __init__(self, labels, conf_threshold: float = 0, iou_threshold: float = 0.5, **kwargs):
        super(BboxConfusionMatrix, self).__init__(num_classes=kwargs.get('num_classes', 2))

        self.labels = labels
        self.label_id2index = {label["id"]: idx for idx, label in enumerate(self.labels)}
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        self.add_state("confmat", default=0)

    def _parse_dt_gt(self, predictions, groundths):
        img_ids = set()
        self._dts = defaultdict(list)
        self._gts = defaultdict(list)

        gts = copy.deepcopy(groundths)
        for gt in gts:
            if gt["image_id"] not in img_ids:
                img_ids.add(gt["image_id"])
            if 'bbox' in gt:
                self._gts[(gt['image_id'])].append(gt)

        for pred in predictions:
            if pred["image_id"] not in img_ids:
                img_ids.add(pred["image_id"])
            self._dts[(pred["image_id"])].append(pred)

        return img_ids

    def update(self, predictions: Dict[str, List[Dict]], references: Dict[str, List[Dict]]) -> None:
        """
        Computes and returns the middle states, such as TP, etc.
        """
        dts, gts = predictions, references
        img_ids = self._parse_dt_gt(dts['bbox'], gts['bbox'])
        confusion_matrix = np.zeros(shape=(self.num_classes + 1, self.num_classes + 1), dtype=np.int64)
        for img_id in img_ids:
            gt = self._gts[img_id]
            dt = self._dts[img_id]
            dt = [d for d in dt if d['score'] > self.conf_threshold]

            if len(gt) == 0 and len(dt) == 0:
                confusion_matrix[self.num_classes, self.num_classes] += 1
            elif len(gt) == 0 and len(dt) > 0:
                for d in dt:
                    confusion_matrix[self.num_classes, self.label_id2index[d['category_id']]] += 1
            elif len(gt) > 0 and len(dt) == 0:
                for g in gt:
                    confusion_matrix[self.label_id2index[g['category_id']], self.num_classes] += 1
            else:
                gt_box = [g['bbox'] for g in gt]
                dt_box = [d['bbox'] for d in dt]

                iscrowd = [int(o['iscrowd']) for o in gt]
                ious = mask_utils.iou(dt_box, gt_box, iscrowd)

                gtind = np.argsort([g['ignore'] for g in gt], kind='mergesort')
                gt = [gt[i] for i in gtind]
                dtind = np.argsort([-d['score'] for d in dt], kind='mergesort')
                dt = [dt[i] for i in dtind]

                iscrowd = [int(o['iscrowd']) for o in gt]
                gtIg = np.array([g['ignore'] for g in gt])
                gtm = np.ones(len(gt)) * -1
                for dind, d in enumerate(dt):
                    m = -1
                    label_m = -1
                    for gind, g in enumerate(gt):
                        if gtm[gind] > 0 and not iscrowd[gind]:
                            continue
                        # if dt matched to reg gt, and on ignore gt, stop
                        if m > -1 and gtIg[m] == 0 and gtIg[gind] == 1:
                            break
                        # continue to next gt unless better match made
                        if ious[dind, gind] < self.iou_threshold:
                            continue
                        m = gind
                        if d["category_id"] == g["category_id"]:
                            label_m = gind
                    if label_m != -1:
                        gtm[label_m] = label_m
                        index = self.label_id2index[g["category_id"]]
                        confusion_matrix[index, index] += 1
                    if m != -1 and label_m < 0:
                        gtm[m] = m
                        g_index = self.label_id2index[g["category_id"]]
                        d_index = self.label_id2index[d["category_id"]]
                        confusion_matrix[g_index, d_index] += 1
                    if m == -1:
                        d_index = self.label_id2index[d["category_id"]]
                        confusion_matrix[self.num_classes, d_index] += 1

                gtm = set(np.asarray(gtm, dtype=np.int32))
                for gind, g in enumerate(gt):
                    if gind not in gtm:
                        g_index = self.label_id2index[g["category_id"]]
                        confusion_matrix[g_index, self.num_classes] += 1

        self.confmat += confusion_matrix

    def compute(self) -> Any:
        """
        Computes the metric by middle states.
        """
        return self.confmat.tolist()



