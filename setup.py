#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as _test

# -----------------------------------------------------------------------------
# CUSTOM COMMANDS
# -----------------------------------------------------------------------------

class CleanCommand(Command):
    """Custom command to tidy up the project root."""
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self):   pass

    def run(self):
        here = os.path.abspath(os.path.dirname(__file__))
        for d in ['build', 'dist'] + [d for d in os.listdir(here) if d.endswith('.egg-info')]:
            path = os.path.join(here, d)
            if os.path.isdir(path):
                print(f"Removing directory: {path}")
                shutil.rmtree(path, ignore_errors=True)

class PyTest(_test):
    """Run pytest on `tests/`."""
    user_options = _test.user_options + [
        ('pytest-args=', 'a', "Arguments to pass to pytest")
    ]
    def initialize_options(self):
        _test.initialize_options(self)
        self.pytest_args = ''
    def finalize_options(self):
        _test.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args.split())
        sys.exit(errno)

# -----------------------------------------------------------------------------
# SETUP()
# -----------------------------------------------------------------------------

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pydeequplus",
    version="0.1.0",
    author="AMIR HOSSEIN ALIKHAH MISHAMANDANI",
    author_email="amirhosseinalikhahm@gatech.edu",
    organization="Neuroligence",
    description="A 100% Python implementation of Amazon Deequ using pandas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/pydeequplus",
    license="Apache-2.0 OR MIT",

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3",
        "numpy>=1.21",
    ],

    extras_require={
        "dev": [
            "pytest>=6.0",
            "flake8",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],

    entry_points={
        # "console_scripts": ["pydeequplus=pydeequplus.cli:main"],
    },

    include_package_data=True,
    zip_safe=False,

    cmdclass={
        'clean': CleanCommand,
        'test': PyTest,
    },
)
