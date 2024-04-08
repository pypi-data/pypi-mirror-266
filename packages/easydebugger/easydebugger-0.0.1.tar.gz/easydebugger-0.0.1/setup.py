from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A clean Python debugging tool'

# Setting up
setup(
    name="easydebugger",
    version=VERSION,
    author="blob2763",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'debugger']
)