#!/usr/bin/env python
##########################################################################
# Copyright (c) 2023 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

from distutils.core import setup

import setuptools  # noqa: F401 - required for command bdist_wheel

version = "1.1.5"

with open("VERSION", "w") as fp:
    fp.write(version)

with open("README.md", "r") as fp:
    readme = fp.read()

# PyPI classifiers: https://pypi.org/classifiers/
setup(
    name="SciDataContainer",
    version=version,
    description="A container class for the storage of scientific data "
    + "together with meta data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Reinhard Caspary",
    author_email="reinhard.caspary@phoenixd.uni-hannover.de",
    url="https://github.com/reincas/scidatacontainer",
    packages=[
        "scidatacontainer",
        "scidatacontainer.tests",
        "scidatacontainer.jsonschema",
    ],
    package_data={"scidatacontainer": ["jsonschema/*"]},
    keywords=["Research Data Management", "Data Container", "Meta Data"],
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=["requests", "jsonschema[format-nongpl]"],
)
