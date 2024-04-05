#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    print_function,
    unicode_literals,
    with_statement,
)

import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = []
with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires += [x.strip() for x in fobj.readlines() if x.strip()]
if os.sys.version_info.major == 3 and os.sys.version_info.minor <= 2:
    with open(
        os.path.join(here, "requirements.py32.txt"), "r", encoding="utf-8"
    ) as fobj:
        requires += [x.strip() for x in fobj.readlines() if x.strip()]

setup(
    name="zenutils",
    version="0.5.4",
    description="Collection of simple utils.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Xin HaoJia",
    maintainer="Xin HaoJia",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["zenutils"],
    install_requires=requires,
    packages=find_packages("."),
    zip_safe=False,
    include_package_data=True,
)
