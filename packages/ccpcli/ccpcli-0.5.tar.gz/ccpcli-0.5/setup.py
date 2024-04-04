###############################################################################
# Copyright (c) 2024-present CorEdge India Pvt. Ltd - All Rights Reserved     #
# Unauthorized copying of this file, via any medium is strictly prohibited    #
# Proprietary and confidential                                                #
# Written by Mani Keshari <mani@coredge.io>, March 2024                       #
###############################################################################
from setuptools import find_packages
from setuptools import setup

setup(
    name='ccpcli',
    version='0.5',
    packages=find_packages(),
    author='Mani Keshari',
    author_email='mani@coredge.io',
    description='CCP cli',
    install_requires=['click', 'halo', 'tabulate'],
    entry_points={
        'console_scripts': [
            'ccpcli=src.cli:cli'
        ]
    }
)
