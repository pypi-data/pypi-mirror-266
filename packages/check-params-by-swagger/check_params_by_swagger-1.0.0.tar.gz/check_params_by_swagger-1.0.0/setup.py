# -*- coding:UTF-8 -*-

"""
 @ProjectName  : check_api_params_by_swagger 
 @FileName     : setup
 @Description  : 
 @Time         : 2024/4/4 下午11:24
 @Author       : Qredsun
 """
import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="check_params_by_swagger",  # 用自己的名替换其中的YOUR_USERNAME_
    version="1.0.0",  # 包版本号，便于维护版本
    author="Qredsun",  # 作者，可以写自己的姓名
    author_email="1410672725@qq.com",  # 作者联系方式，可写自己的邮箱地址
    description="check param by swagger",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # 对python的最低版本要求
)