# coding=utf-8
from setuptools import setup, find_packages

setup(
    name='TerraLib',  # 包名
    version='1.0.4',  # 版本
    description="Common libs for use, include operation on excel, print and so on.",  # 包简介
    long_description=open('README.md', encoding="utf-8").read(),  # 读取文件中介绍包的详细内容
    include_package_data=True,  # 是否允许上传资源文件
    author='TerraJuly',  # 作者
    author_email='caijie_hui@163.com',  # 作者邮件
    maintainer='TerraJuly',  # 维护者
    maintainer_email='caijie_hui@163.com',  # 维护者邮件
    license='MIT License',  # 协议
    url='',  # github或者自己的网站地址
    packages=find_packages(),  # 包的目录
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',  # 设置编写时的python版本
        'Programming Language :: Python :: 3.9',  # 设置编写时的python版本
        'Programming Language :: Python :: 3.10',  # 设置编写时的python版本
    ],
    python_requires='>=3.6',  # 设置python版本要求
    install_requires=['xlrd>=1.2.0', 'openpyxl>=3.0.0']  # 安装所需要的库

)
