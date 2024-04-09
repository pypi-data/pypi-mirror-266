# -*- coding: utf-8 -*-
# @Time    : 2023/4/9 18:21
# @Author  : luyi
from setuptools import setup
setup(
    name="mipx",
    version="0.2.16",
    author="ly",
    author_email="2662017230@qq.com",
    description="mipx",
    url="https://github.com/bme6/mipx",
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    # packages=find_packages(exclude=['core', '__pycache__']),
    packages=['mipx'],
    long_description="mip tools",
    include_package_data=True,
    install_requires=[
        'ortools',
        "docplex"
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)
