from enum import Enum
from functools import wraps
import os.path


class CacheType(Enum):
    PICKLE = "pkl"
    JOBLIB = "lib"


def cache_wrapper(prefix, save_path=None, force_write=False, use: CacheType = CacheType.PICKLE):
    """
    装饰器，训练完保存模型，如果模型存在则加载。
    :param prefix: 保存的文件名
    :param force_write: 强行刷新模型
    :param save_path: 模型保存位置
    :param use: 使用的方法: pickle/joblib
    """

    # 外层为了获取 save_path 参数
    # wrapper 才是真正的装饰器
    def wrapper(train_func):
        """

        :param train_func: 训练模型的函数
        """

        @wraps(train_func)
        def inner(*args, **kwargs):
            args_append = "_".join([str(arg) for arg in args])
            kwargs_append = "_".join([f'{k}_{v}' for k, v in kwargs.items()])
            suffix = 'pkl' if use == CacheType.PICKLE else 'lib' if use == CacheType.JOBLIB else ''

            format_filename = f'{prefix}_{args_append}_{kwargs_append}.{suffix}'

            if save_path is not None:
                _try_make_dirs(save_path)
                real_filename = os.path.join(save_path, format_filename)
            else:
                real_filename = format_filename
            if force_write or not os.path.exists(real_filename):
                # 强制写入或者没有缓存
                # 执行并保存
                model = train_func(*args, **kwargs)
                if use == CacheType.JOBLIB:
                    import joblib
                    joblib.dump(model, real_filename)
                    print(f'任务完成, 保存{type(model)} -> {real_filename} ({use})')
                elif use == CacheType.PICKLE:
                    import pickle
                    with open(real_filename, 'wb') as f:
                        pickle.dump(model, f)
                        print(f'任务完成, 保存{type(model)} -> {real_filename} ({use})')
                else:
                    raise ValueError(f'未知的保存模型方式{use}')
                return model
            else:
                # 加载
                if use == CacheType.JOBLIB:
                    import joblib
                    ret = joblib.load(real_filename)
                    print(f'加载模型 {type(ret)} <-- "{real_filename}" ({use}).')
                    return ret
                if use == CacheType.PICKLE:
                    import pickle
                    with open(real_filename, 'rb') as f:
                        ret = pickle.load(f)
                        print(f'加载模型 {type(ret)} <-- "{real_filename}" ({use}).')
                        return ret

                raise ValueError(f'未知的保存模型方式{use}')

        return inner

    return wrapper


def _try_make_dirs(path):
    if not os.path.exists(path):
        # 创建文件夹
        os.makedirs(path)
        print(f"创建缓存文件夹: {path}")
