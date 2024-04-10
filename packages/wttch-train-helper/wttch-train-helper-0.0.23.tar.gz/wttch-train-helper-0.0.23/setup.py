from distutils.core import setup

setup(
    name='wttch-train-helper',
    version='0.0.23',
    description="Wttch's Train Helper",
    author="wttch",
    packages=[
        'wth',
        'wth.data',
        'wth.notification',
        'wth.torch',
        'wth.torch.utils',
        'wth.utils',
    ],
    package_dir={
        '': 'src/wttch-train-helper'
    },
    requires=['torch', 'numpy', 'prettytable']
)
