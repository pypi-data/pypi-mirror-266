# from distutils.core import setup
from setuptools import setup, find_packages

# packages = ['gxl_ai_utils', 'gxl_ai_utils.utils',
#             'gxl_ai_utils.config', 'gxl_ai_utils.run',
#             'gxl_ai_utils.thread' ]
setup(name='gxl_ai_utils',
      version='1.3.4',
      author='Xuelong Geng',
      description='这个是耿雪龙的工具包模块, update time: 2024-4-9',
      author_email='3349495429@qq.com',
      packages=find_packages(),
      package_dir={'requests': 'requests'}, )
