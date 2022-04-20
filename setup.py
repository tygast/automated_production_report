# -*- coding: utf-8 -*-
"""Run Setup Script to build Production and Consumption reports"""
import re

from setuptools import setup

with open("src/reports/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    version=version,
    description=(
        "A set of programs meant to be run on a schedule to" 
        "generate consumption and production reports for"
        "division locations and unit operations"
    ),
)
