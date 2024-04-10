from typing import Optional

from tqdm import tqdm

# 当前进度/总进度|进度条|进度百分比 [用时<剩余用时, 平均用时 单位] 描述
bar_format = "{n_fmt}/{total_fmt}|{bar}|{percentage:3.0f}%［{elapsed}<{remaining},{rate_fmt}{postfix}]{desc}"


class Progress(tqdm):
    """
    使用 tqdm 包装的进度条, 修改下格式, 方便训练用.
    """

    def __init__(self, iterable=None, total=None, ncols=120):
        """
        构造函数
        Args:
            iterable: 可以对进度条进行迭代，自动推进进度条
            total: 总条目数
            ncols: 进度条总宽度, 默认120.
        """
        super().__init__(iterable=iterable, total=total, ncols=ncols, bar_format=bar_format)

    def train_result(self, loss: Optional[float] = None, acc: Optional[float] = None):
        """
        设置训练结果，同时将进度条推进 1 个条目。
        Args:
            loss: 损失函数，可空
            acc: 精确度，可空 (0-1)

        """
        desc_str = ""
        if loss is not None:
            desc_str += f" - Loss: {loss:.6f}"
        if acc is not None:
            desc_str += f" - Acc: {acc * 100:5.2f}%"
        self.set_description_str(desc_str)
        if self.iterable is None:
            # 如果不是自动迭代，推进1
            self.update(1)
