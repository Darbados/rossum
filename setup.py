#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="elisctl",
    version="2.9.0",
    description="Command line interface for controlling the Rossum platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://developers.rossum.ai/",
    author="Rossum developers",
    author_email="support@rossum.ai",
    license="MIT",
    project_urls={
        "Source": "https://github.com/rossumai/elisctl",
        "Tracker": "https://github.com/rossumai/elisctl/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests*",)),
    install_requires=[
        "pandas",
        "click",
        "click-shell",
        "xlrd",
        "requests",
        "jsondiff",
        "tabulate",
        'dataclasses;python_version<"3.7"',
        "openpyxl>=2.6",
        "jmespath",
        "polling2",
    ],
    python_requires=">=3.6",
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov", "requests_mock", "pytest-click"],
    zip_safe=False,
    entry_points={"console_scripts": ["elisctl = elisctl.main:entry_point"]},
)
