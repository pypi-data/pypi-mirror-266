from typing import Optional, Union
import threading

import torch

from torch import nn

# 线程保存的 device
_device_local = threading.local()


def try_gpu(device_no: Optional[int] = None) -> torch.device:
    """
    尝试获取 GPU 设备。
    先获取 cuda，没有选择 mps，还没有使用 cpu。
    :param device_no: 设备号，只对 cuda 有效
    :return: GPU 设备
    """
    if torch.cuda.is_available():
        if device_no is not None and device_no < torch.cuda.device_count():
            #
            return torch.device(f'cuda:{device_no}')

        return torch.device('cuda')
    return torch.device('mps' if torch.mps else 'cpu')


def set_device_local(device: torch.device):
    """
    设置线程变量：训练用设备
    :param device: 训练用设备
    """
    _device_local.device = device
    print(f'设置线程变量 device = {device.type}:{device.index} [{threading.currentThread().name}]')


def get_device_local() -> torch.device:
    """
    获取线程变量：训练用设备
    :return: 训练用设备
    """
    device = getattr(_device_local, 'device', None)
    if device is None:
        device = try_gpu()
        set_device_local(device)
    return device


def set_dtype_local(dtype: torch.dtype):
    """
    设置线程变量：训练数据类型
    Args:
        dtype: 训练用数据类型
    """
    _device_local.dtype = dtype

    print(f'设置线程变量 dtype = {dtype} [{threading.currentThread().name}]')


def get_dtype_local():
    dtype = getattr(_device_local, 'dtype', None)
    if dtype is None:
        dtype = torch.float
        set_dtype_local(dtype)
        print(f'线程变量 dtype 为空，已设置为 {dtype}.')
    return dtype


def module_to(module: nn.Module) -> nn.Module:
    """
    将模型转换为线程的设备类型
    Args:
        module: 要转换的模型

    Returns:
        模型本身
    """
    return module.to(get_device_local())


def tensor_to(*data: torch.Tensor) -> Union[list[torch.Tensor], torch.Tensor]:
    """
    将数据 tensor 或者 tensor 列表 转换为线程保存的设备类型。
    Args:
        data: 要转换的数据。

    Returns:
        数据的转换结果。
    """
    ret = [i.to(get_device_local()) for i in data]
    if len(ret) == 1:
        return ret[0]
    return ret
