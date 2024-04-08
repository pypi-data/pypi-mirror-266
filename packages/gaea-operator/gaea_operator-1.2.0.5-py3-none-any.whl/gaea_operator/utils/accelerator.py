#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/27
# @Author  : yanxiaodong
# @File    : accelerator.py
"""
from abc import ABCMeta, abstractmethod


class Accelerator(metaclass=ABCMeta):
    """
    Accelerator
    """
    T4 = "T4"
    V100 = "V100"
    A100 = "A100"
    R200 = "R200"

    NVIDIA = "Nvidia"
    KUNLUN = "Kunlun"

    def __init__(self, name: str = "T4"):
        self.name = name
        self.image = ""
        self.args = None
        self.env = None

    def suggest_image(self):
        """
        Suggest image
        """
        return self.image

    def suggest_env(self):
        """
        Suggest env
        """
        return self.env

    def suggest_args(self):
        """
        Suggest args
        """
        return self.args

    @abstractmethod
    def suggest_flavours(self):
        """
        Suggest flavours
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        raise NotImplementedError()


class NvidiaAccelerator(Accelerator):
    """
    Nvidia Accelerator
    """

    def __init__(self, name: str = "T4"):
        super().__init__(name=name)
        self.image = "iregistry.baidu-int.com/windmill-public/inference/nvidia:v1.2.0.1"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH":
                    "/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/opt/tritonserver/lib",
                "PATH": "/opt/tritonserver/bin:/usr/local/mpi/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:"
                        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = ['c4m16gpu1',
                        'c8m32gpu1',
                        'c8m32gpu2',
                        'c16m64gpu2',
                        'c16m32gpu4',
                        'c16m64gpu4',
                        'c32m96gpu4']
        return flavour_list

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        resource = {"accelerator": self.name,
                    "gpu": "75",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "args": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        return ["config.maxResources.scalarResources.nvidia.com/gpu>1"]


class KunlunAccelerator(Accelerator):
    """
    Kunlun Accelerator
    """

    def __init__(self, name: str = "R200"):
        super().__init__(name=name)
        self.image = "iregistry.baidu-int.com/windmill-public/inference/kunlun:v1.2.0"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH":
                    "/opt/tritonserver/backends/paddlelite:/opt/tritonserver/backends/Kunlun:$LD_LIBRARY_PATH",
                "XTCL_L3_SIZE": "16776192"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = ['c4m16xpu1']
        return flavour_list

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """

        resource = {"accelerator": self.name,
                    "gpu": "7500",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "backend": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        return ["config.maxResources.scalarResources.baidu.com/xpu-mem>1"]


def get_accelerator(name: str = None, kind: str = None) -> Accelerator:
    """
    Get accelerator.
    """
    if kind == Accelerator.NVIDIA:
        return NvidiaAccelerator(name=name)
    if kind == Accelerator.KUNLUN:
        return KunlunAccelerator(name=name)

    if name in (Accelerator.T4, Accelerator.V100, Accelerator.A100):
        return NvidiaAccelerator(name=name)
    elif name in (Accelerator.R200, ):
        return KunlunAccelerator(name=name)
    else:
        raise Exception("Unsupported accelerator: {}".format(name))