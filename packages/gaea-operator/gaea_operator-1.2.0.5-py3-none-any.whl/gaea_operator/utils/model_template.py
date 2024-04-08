#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/27
# @Author  : yanxiaodong
# @File    : algorithm.py
"""
from abc import ABCMeta, abstractmethod
from windmillmodelv1.client.model_api_modelstore import parse_modelstore_name
from windmillmodelv1.client.model_api_model import ModelName


class ModelTemplate(metaclass=ABCMeta):
    """
    Algorithm class
    """
    PPYOLOE_PLUS_NAME = 'ppyoloe_plus'
    RESNET_NAME = 'resnet'

    def __init__(self, model_store_name: str):
        model_store = parse_modelstore_name(model_store_name)
        self.workspace_id = model_store.workspace_id
        self.model_store_name = model_store.local_name

    @abstractmethod
    def suggest_template_preprocess(self):
        """
        Get template name for preprocess
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_template_postprocess(self):
        """
        Get template name for postprocess
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_template_model(self):
        """
        Get template name for model
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_template_ensemble(self):
        """
        Get template name for ensemble
        """
        raise NotImplementedError()


class PPYOLOEPLUSTemplate(ModelTemplate):
    """
    PPYOLOE_PLUS Algorithm class
    """
    def __init__(self, model_store_name):
        super(PPYOLOEPLUSTemplate, self).__init__(model_store_name=model_store_name)

    def suggest_template_preprocess(self):
        """
        Get template name for preprocess
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="ppyoloeplus-preprocess")
        return model_name.get_name()

    def suggest_template_postprocess(self):
        """
        Get template name for postprocess
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="ppyoloeplus-postprocess")
        return model_name.get_name()

    def suggest_template_model(self):
        """
        Get template name for model
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="ppyoloeplus-model")
        return model_name.get_name()

    def suggest_template_ensemble(self):
        """
        Get template name for ensemble
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="ppyoloeplus-ensemble")
        return model_name.get_name()


class ResNetTemplate(ModelTemplate):
    """
    ResNet Algorithm class
    """
    def __init__(self, model_store_name):
        super(ResNetTemplate, self).__init__(model_store_name=model_store_name)

    def suggest_template_preprocess(self):
        """
        Get template name for preprocess
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="single-attr-cls-preprocess")
        return model_name.get_name()

    def suggest_template_postprocess(self):
        """
        Get template name for postprocess
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="single-attr-cls-postprocess")
        return model_name.get_name()

    def suggest_template_model(self):
        """
        Get template name for model
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="single-attr-cls-model")
        return model_name.get_name()

    def suggest_template_ensemble(self):
        """
        Get template name for ensemble
        """
        model_name = ModelName(workspace_id=self.workspace_id,
                               model_store_name=self.model_store_name,
                               local_name="single-attr-cls-ensemble")
        return model_name.get_name()


def get_model_template(name: str, model_store_name: str):
    """
    Get algorithm class by name
    """
    if name == ModelTemplate.PPYOLOE_PLUS_NAME:
        return PPYOLOEPLUSTemplate(model_store_name=model_store_name)
    elif name == ModelTemplate.RESNET_NAME:
        return ResNetTemplate(model_store_name=model_store_name)
    else:
        raise NotImplementedError(f'Algorithm {name} not supported')