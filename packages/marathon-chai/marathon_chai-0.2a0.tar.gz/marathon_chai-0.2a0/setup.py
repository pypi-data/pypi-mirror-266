# -*- coding: utf-8 -*-
"""
setup.py

python_chai
"""

from setuptools import setup, find_packages


VERSION = "0.2a"
DESCRIPTION = "Python driver for Marathon CHAI interface"
LONG_DESCRIPTION = "Base functionality"


setup(
    name="marathon_chai",
    version=VERSION,
    author="KirichRus",
    author_email="kirichrus@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "python-can",
    ],
    entry_points = {
        'can.interface': [
            'chai = marathon_chai.canlib:ChaiBus'
        ]
    }
)
