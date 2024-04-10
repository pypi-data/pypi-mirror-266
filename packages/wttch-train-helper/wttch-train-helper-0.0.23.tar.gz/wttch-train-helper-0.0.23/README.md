# wttch 的 AI 训练工具包

## 一、消息通知

### 1.1 钉钉 webhook 通知

[钉钉 webhook 机器人API](https://open.dingtalk.com/document/orgapp/robot-message-types-and-data-format#title-z74-8to-i7e)

```python
from wth.notification import DingtalkNotification

# 钉钉机器人 webhook 的链接
webhook_url = ''
# 消息签名的密钥
secret = ''

notification = DingtalkNotification(webhook_url, secret)

# 发送文本通知
notification.send_text("")
# 发送markdown
notification.send_markdown('')
```

### 1.2 企业微信 webhook 通知

[企业微信机器人API](https://developer.work.weixin.qq.com/document/path/91770)

```python
from wth.notification import WechatNotification

# 企业微信机器人 webhook 的链接
webhook_url = ''
notification = WechatNotification(webhook_url)

# 发送文本通知
notification.send_text("")
# 发送markdown
notification.send_markdown('')
```

## 二、训练工具包

### 2.1 缓存工具

> 不需要修改太多代码就可以帮助你缓存数据到指定的缓存文件去。
>
> (1). 添加 cache_wrapper;
> (2). 正常调用你的函数。

```python
from wth.utils import cache_wrapper

# 缓存的文件名字前缀，函数的参数会被添加到该名字后面
prefix = 'dataset'
# 缓存的文件夹位置
save_path = './dataset_cache'


@cache_wrapper(prefix=prefix, save_path=save_path)
def you_load_dataset_function():
    return {'a': 1, 'b': 2}


you_load_dataset_function()
```

### 2.2 计时器

```python
from wth.utils import StopWatch

stopwatch = StopWatch()
stopwatch.start("job 1")
# 费时操作
stopwatch.stop()
stopwatch.start("job 2")
# 费时操作
stopwatch.stop()

# 格式化打印
stopwatch.display()
```

## 2.3 进度条

简单包装了 `tqdm` 工具。

固定一种还不错的进度条格式。

### 2.3.1 循环模式

```python
from wth.utils.progress import Progress

with Progress(total=1000) as progress:
    for i in range(1000):
        # 在这里训练

        # 进度条末尾显示训练结果
        progress.train_result(loss=0.01, acc=0.02)
```

### 2.3.2 迭代器模式

```python
from wth.utils.progress import Progress

dataset = [1, 2, 3]

progress = Progress(dataset)

for data in progress:
    # 使用 data 进行训练

    # 进度条末尾显示训练结果
    progress.train_result(loss=0.01, acc=0.02)
```

## 2.4 快捷获取函数执行时间
```python
from wth.utils import get_time
from time import sleep

@get_time
def test():
    sleep(1)
```
执行结果:
>"test()" took 1.0051 seconds to execute.

## 三、torch 工具包

### 3.1 训练设备获取

#### 3.1.1 获取设备

先尝试获取 cuda, 如果不支持获取 mps(macOS), 还不支持就 cpu。

可以添加 `device_no` 参数，但是只对 cuda 有效，表示 cuda 的序号。

```python
from wth.torch.utils import try_gpu

try_gpu(device_no=2)
```

#### 3.1.2 ThreadLocal 的设备变量的设置、获取

1. 将使用的设备写入 thread local;
2. 需要训练设备的地方, 从 thread local 中获取设备数据;

```python
from wth.torch.utils import try_gpu, get_device_local, set_device_local

# 尝试获取 gpu 并写入 thread local
set_device_local(try_gpu(device_no=0))

# 从 thread local 读取设备
device = get_device_local()

```

### 3.2 ThreadLocal 的训练类型 dtype 的设置、获取

1. 将使用的 dtype 写入 thread local;
2. 需要训练类型的地方, 从 thread local 中获取设备数据;

```python
import torch
from wth.torch.utils import get_dtype_local, set_dtype_local

# 将训练的 dtype 数据类型写入 thread local
set_dtype_local(torch.float32)

# 从 thread local 读取数据类型
dtype = get_dtype_local()
```

### 3.3 yml 多环境配置

环境配置，使用 yml 文件。

#### 首先书写你的 yml 文件

例如:

```yaml
# 激活的环境
active: local

# 本地环境
local:
  epochs: 10
  batch-size: 256
  dataset-path: /Volumes/Wttch/datasets/torchvision/cache
  dtype: float32
  cuda-no: 1
  # 你的其他属性


# 学校环境
school-server:
  epochs: 10
  batch-size: 256
  dataset-path:
```

active 必需标识启用的环境。
后续使用
key: 环境配置
的方式可以定义多个环境。

#### 获取你启用的环境的变量

```python
# 获取你的配置
from wth.torch import Config

# 定义配置
config = Config()

# 获取预定义的属性
print(config.epochs)

# 获取其他你自己的属性
print(config['you-property-key'])
```

### 3.4 TrainAndTestDataLoader 测试和训练集

```python
from wth.torch.utils.data import TrainAndTestDataLoader
from torch.utils.data import Dataset, DataLoader

# 数据集声明, 需要是 Dataset 的子类
dataset = ...  # type: Dataset

# train_rate 训练用集合的百分比
loader = TrainAndTestDataLoader(dataset, train_rate=0.8)

# 训练用 DataLoader
loader1 = loader.train_loader  # type: DataLoader
loader2 = loader.test_loader  # type: DataLoader
```