import random
from typing import Union

import numpy as np

#
# def seq_data_iter_random(corpus: np.ndarray, batch_size: int, seq_len: int, label=False) \
#         -> Union[tuple[np.ndarray, np.ndarray], np.ndarray]:
#     """
#     随机生成序列数据，只保证序列内的顺序和原始顺序一致，不能保证小批量数据之间连续。
#     Args:
#         corpus: 原始语料库
#         batch_size: 批处理大小
#         seq_len: 序列长度
#
#     Returns:
#
#     """
#     # 偏移
#     corpus = corpus[random.randint(0, seq_len):]
#     # -1, 因为标签 +1, 序列的下一个数据就是标签
#     num_seqs = (len(corpus) - (1 if label else 0)) // seq_len
#     # 抽样开始的位置
#     init_indices = list(range(0, num_seqs * seq_len, seq_len))
#     # 打乱, batch 内序列不一定连续
#     random.shuffle(init_indices)
#
#     def get_data(pos):
#         return corpus[pos: pos + seq_len]
#
#     # 可以生成多少批数据
#     num_batches = num_seqs // batch_size
#     for i in range(0, batch_size * num_batches, batch_size):
#         init_indices_per_batch = init_indices[i:i + batch_size]
#         X = [get_data(j) for j in init_indices_per_batch]
#         if label:
#             Y = [get_data(j + 1) for j in init_indices_per_batch]
#             yield np.array(X), np.array(Y)
#         else:
#             yield np.array(X)
#
#
# def seq_data_iter_sequential(corpus: np.ndarray, batch_size: int, seq_len: int, label: bool = False) \
#         -> Union[tuple[np.ndarray, np.ndarray], np.ndarray]:
#     """
#     顺序生成序列数据，能保证小批量数据之间连续。
#     Args:
#         corpus: 原始语料库
#         batch_size: 批处理大小
#         seq_len: 序列长度
#
#     Returns:
#
#     """
#     corpus = corpus[random.randint(0, seq_len):]
#     num_tokens = ((len(corpus) - (1 if label else 0)) // batch_size) * batch_size
#
#     Xs = corpus[0: num_tokens]
#     Xs = Xs.reshape(batch_size, -1)
#     if label:
#         Ys = corpus[1: num_tokens + 1]
#         Ys = Ys.reshape(batch_size, -1)
#
#     num_batches = Xs.shape[1] // seq_len
#     for i in range(0, seq_len * num_batches, seq_len):
#         X = Xs[:, i: i + seq_len]
#         if label:
#             Y = Ys[:, i: i + seq_len]
#             yield X, Y
#         else:
#             yield X
#
#
# class SeqDataGenerator:
#
#     def __init__(self, data: np.ndarray, batch_size: int, seq_len: int, shuffle: bool = True, label: bool = False):
#         """
#         序列数据生成器。
#         Args:
#             data: 原始数据
#             batch_size: 批处理长度
#             seq_len: 序列长度
#             shuffle: 批之间收否随机
#         """
#         # 分开处理是因为使用 yield, 也可以同一个函数处理，之后随机一下
#         self.data_iter_fn = seq_data_iter_random if shuffle else seq_data_iter_sequential
#
#         self.data = data
#         self.batch_size = batch_size
#         self.seq_len = seq_len
#         self.label = label
#
#     def __iter__(self):
#         return self.data_iter_fn(self.data, self.batch_size, self.seq_len, self.label)


class SeqDataLoader:
    def __init__(self, data: np.ndarray, seq_len: int, label: bool = False):
        """
        序列数据加载器。
        Args:
            data: 原始数据
            seq_len: 序列长度
            label: 是否生成 label: 对 x 向后偏移一位, 即预测的下一个
        """
        self.data = data
        self.seq_len = seq_len
        self.label = label

    def get_data(self):
        data = self.data[random.randint(0, self.seq_len):]

        num_seqs = (len(data) - (1 if self.label else 0)) // self.seq_len * self.seq_len

        x_data = data[0:num_seqs]
        y_data = data[1: num_seqs + 1]

        if self.label:
            return x_data.reshape((-1, self.seq_len,) + x_data.shape[1:]), y_data.reshape(
                (-1, self.seq_len,) + x_data.shape[1:])

        return x_data.reshape((-1, self.seq_len,) + x_data.shape[1:])
