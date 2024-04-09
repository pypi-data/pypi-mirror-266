#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, "__init__.py")).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


version = get_version("regex_match")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
install_requires = [
    "inflection>=0.3.0",
    "django-polymorphic==1.3",
    "funcy==1.4",
    "purl==1.0.3",
    "toolz==0.12.0",
]

setup(
    name="django-regex-match",
    version=version,
    packages=get_packages("regex_match"),
    include_package_data=True,
    license="",  # example license
    description="",
    url="http://www.admetricks.com/",
    author="Dev Admx",
    author_email="dev@admetricks.com",
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",  # example license
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        # Replace these appropriately if you are stuck on Python 2.
    ],
)
