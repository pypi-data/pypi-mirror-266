#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from setuptools import find_packages, setup


# Package meta-data.
NAME = 'kitchen_ware_classification_cnn_model'
DESCRIPTION = "Convulational neural model package from Train In Data."
URL = "https://github.com/chibuikeeugene/kitchen_ware_classification_cnn/"
EMAIL = "chibuikeeugene@gmail.com"
AUTHOR = "Eugene"
REQUIRES_PYTHON = ">=3.6.0"

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the
# Trove Classifier for that!
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory to sys.path
sys.path.append(current_dir)


# What packages are required for this module to be executed?
def list_reqs(fname='requirements.txt'):
    with open(fname) as fd:
        return fd.read().splitlines()

from cnn_model_package.config.core import PACKAGE_ROOT

with open(os.path.join(PACKAGE_ROOT, 'VERSION')) as _version_file:
    __version__ = _version_file.read().strip()

long_description = DESCRIPTION

# Where the magic happens:
setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    package_data={'cnn_model_package': ['VERSION']},
    install_requires=list_reqs(),
    extras_require={},
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
