#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tg_flask_sse_common',
    version='2.0.9',
    author='Tangshimin',
    description='tg_flask_sse_common',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        'tg_flask_sse_common'
    ],
    requires=['redis'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
