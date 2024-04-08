import os
import io
from setuptools import setup, find_packages

with io.open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

with io.open("requirements.txt", 'r') as f:
    install_requires = f.read().split(os.sep)


setup(
    name='pyresp',
    version='1.0.3',
    description='fastapi的通用返回助手',
    author='buyfakett',
    author_email='buyfakett@vip.qq.com',
    license='MIT',
    url="https://github.com/buyfakett",
    packages=find_packages(),  # packages=["pytest"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=True,
    python_requires='>=3.6',
    install_requires=install_requires,
)
