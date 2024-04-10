import threading
from time import sleep

import torch

from wth.utils import StopWatch
from wth.utils import cache_wrapper
from wth.torch.utils import get_device_local, set_device_local, try_gpu, set_dtype_local, get_dtype_local


def set_device(device):
    set_device_local(device)


thread1 = threading.Thread(target=set_device, args=[try_gpu()])
thread2 = threading.Thread(target=set_device, args=[try_gpu()])

thread1.start()
thread2.start()


def set_dtype(dtype):
    set_dtype_local(dtype)
    print(get_dtype_local())


thread1 = threading.Thread(target=set_dtype, args=[torch.float32])
thread2 = threading.Thread(target=set_dtype, args=[torch.float])

thread1.start()
thread2.start()
