from setuptools import setup, find_packages
from os import path
import json
import sys

here = path.abspath(path.dirname(__file__))
root = path.dirname(here)

setup(
    name='ttxt',
    version='0.0.5.8',
    description='TT exchange interfacing library',
    author='sus',
    packages=find_packages(),
)