import json
import sys

import yaml


class Config:
    """
    环境配置，使用 yml 文件。
    例如:
    ```
    active: local
      school-server:
      local:
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
        with open(config_file) as f:
            self.original = yaml.load(f, Loader=yaml.FullLoader)
            self.active_profile = self.original['active']
            if self.active_profile is None:
                raise ValueError("No active profile")

            print(f"Active profile[{self.active_profile}].")
            sys.stdout.flush()

            self.configs = self.original[self.active_profile]  # type: dict
            if self.configs is None:
                print(f"Active profile[{self.active_profile}] has no arguments.", file=sys.stderr)
                sys.stderr.flush()
                self.configs = {}

    def __getitem__(self, item):
        if self.configs.__contains__(item):
            return self.configs[item]
        key = item.replace("_", "-")
        if self.configs.__contains__(key):
            return self.configs[key]
        return None

    def __str__(self):
        return json.dumps(self.original)
