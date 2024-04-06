#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages
import pybi as pbi
from pathlib import Path


def all_static_files():
    files = [str(p) for p in Path("pybi/static").glob("*.*")]
    return files


with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

requirements = ["pandas", "simplejson", "jinja2", "typing_extensions"]

test_requirements = ["pytest>=3", "playwright", "pyecharts"]

setup(
    author="carson_jia",
    author_email="568166495@qq.com",
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="...",
    entry_points={
        # 'console_scripts': [
        #     'test_prj=test_prj.cli:main',
        # ],
    },
    install_requires=requirements,
    license="MIT license",
    # long_description=readme,
    include_package_data=True,
    keywords=["pybi", "vision", "BI", "report"],
    name="pybi-next",
    packages=find_packages(include=["pybi", "pybi.*"]),
    data_files=[
        (
            "template",
            [
                "pybi/template/index.html",
            ],
        ),
        (
            "static",
            all_static_files(),
        ),
    ],
    test_suite="__tests",
    tests_require=test_requirements,
    url="",
    version=pbi.__version__,
    zip_safe=False,
)
