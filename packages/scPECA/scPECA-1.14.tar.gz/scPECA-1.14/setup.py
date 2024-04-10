from setuptools import setup, find_packages
import os
import shutil
from setuptools.command.install import install
import subprocess
import urllib.request

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='scPECA',
    version='1.14',
    author='Jiahao Zhang',
    author_email='zhangjiahao@amss.ac.cn',
    description='PECA2 gene regulatory network construction for single-cell data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zhangjiahao1234/scPECA',
    packages=find_packages(),
    package_data={'': ['./Prior/*', './Cones/*', './Data/*']},
    include_package_data=True,
    # cmdclass={'install':  CustomInstallCommand}
)