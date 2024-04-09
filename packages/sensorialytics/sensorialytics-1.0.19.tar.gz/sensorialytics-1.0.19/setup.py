#  setup.py
#  Project: sensorialytics
#  Copyright (c) 2024 Sensoria Health Inc.
#  All rights reserved

from setuptools import setup, find_packages

VERSION = '1.0.19'

setup(
    name='sensorialytics',
    packages=find_packages(),
    version=VERSION,
    license='MIT',
    description='Sensoria python library',
    author='Stefano Rossotti',
    author_email='stefano@sensoriainc.com',
    keywords=['sensoria', 'analytics'],
    install_requires=[
        "numpy>=1.16.5",
        "requests",
        "requests-oauthlib",
        "fitdecode",
        "sklearn",
        "pandas>=1.1.3",
        "matplotlib>=3.3.2",
        "scipy>=1.5.2",
        "opencv-python",
        "seaborn",
        "xgboost",
        "keras",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
