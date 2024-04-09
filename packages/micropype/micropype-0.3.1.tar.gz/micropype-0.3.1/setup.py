#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


setup(
    name="micropype",
    version="0.3.1",
    packages=find_packages(),
    author="Bastien Cagna",
    description="Very basic pipelining toolbox",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='BSD 3',
    entry_points = {},
    install_requires=["colorama"],
    extras_require={ "dev": [ "pytest" ]},
    include_package_data=True,
)
