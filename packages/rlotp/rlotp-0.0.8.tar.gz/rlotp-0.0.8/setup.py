# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
from codecs import open
from setuptools import setup, find_packages

app_name = 'rlotp'

sys.path[0:0] = ['src/'+app_name]

from version import __version__

def get_readme(filename):
    content = ""
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as readme:
            content = readme.read()
    except Exception as e:
        pass
    return content

setup(
    name=app_name,
    version=__version__,
    author="Md. Jahidul Hamid & PyOTP contributors",
    author_email="jahidulhamid@yahoo.com",
    url="https://github.com/rlotp/rlotp",
    project_urls={
        "Documentation": "https://neurobin.github.io/rlotp",
        "Source Code": "https://github.com/neurobin/rlotp",
        "Issue Tracker": "https://github.com/neurobin/rlotp/issues",
        "Change Log": "https://github.com/neurobin/rlotp/blob/master/Changes.rst",
    },
    license="MIT License",
    description="Random Length OTP Library in Python",
    long_description=get_readme("README.rst"),
    python_requires=">=3.7",
    install_requires=[],
    # extras_require={
    #     "test": ["coverage", "wheel", "ruff", "mypy"],
    # },
    packages=["rlotp"],
    package_dir={"": "src"},
    # package_data={"rlotp": ["py.typed"]},
    # platforms=["MacOS X", 'GNU/Linux', "Posix"],
    zip_safe=False,
    # test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        # "Operating System :: MacOS :: MacOS X",
        # "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
