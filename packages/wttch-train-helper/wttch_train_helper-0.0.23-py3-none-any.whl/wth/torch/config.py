import torch

from .utils import try_gpu, set_device_local, set_dtype_local
from ..utils.config import Config as _Config


class Config(_Config):
    """
    环境配置，使用 yml 文件。
    例如:
    ```
    active: local
      school-server:
      local:
        epochs: 10
        batch-size: 64
        dtype: float32
        cuda_no: 1
        dataset_path: /your/dataset/path
    ```
    active 必需标识启用的环境。
    后续使用 key: 环境配置的方式可以定义多个环境。
    """

    def __init__(self, config_file='config.yml'):
        """
        构造函数。
        Args:
            config_file: 配置文件所在位置，默认 config.yml。
        """
        super(Config, self).__init__(config_file=config_file)
        self.epochs = self.configs.get('epochs', 10)
        self.batch_size = self.configs.get('batch-size', 64)
        self.dtype = self.configs.get('dtype', 'float32')
        self.cuda_no = self.configs.get('cuda-no')
        self.dataset_path = self.configs.get('dataset-path')

        # 设置设备
        if self.cuda_no is not None:
            set_device_local(try_gpu(self.cuda_no))
        # 设置 dtype
        if self.dtype is not None:
            if self.dtype == 'float32':
                set_dtype_local(torch.float32)
            else:
                set_dtype_local(torch.float64)
