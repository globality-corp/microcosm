#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm"
version = "3.1.0"

setup(
    name=project,
    version=version,
    description="Microcosm - Simple microservice configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "contextdecorator>=0.10.0",
        "inflection>=0.3.1",
        "lazy>=1.3",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    extras_require={
        "test": [
            "nose>=1.3.7",
            "PyHamcrest",
            "coverage",
        ],
        "lint": [
            "flake8<5",
            "flake8-print",
            "flake8-logging-format",
            "flake8-isort"
        ]
    },
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "hello_world = microcosm.example:create_hello_world",
            "opaque = microcosm.opaque:configure_opaque",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "PyHamcrest>=1.8.5",
    ],
)
