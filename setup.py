#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm"
version = "4.1.0"

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
    package_data={
        "microcosm": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.9",
    keywords="microcosm",
    install_requires=[
        "importlib-metadata>=3.6",
        "inflection>=0.5.1",
        "lazy>=1.6",
    ],
    extras_require={
        "build": [
            "coverage>=7.3.2",
            "flake8-isort>=6.1.1",
            "flake8-logging-format>=1.0.0",
            "flake8-print>=5.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "PyHamcrest>=2.1.0",
            "pytest-cov>=4.1.0",
            "pytest>=7.4.3",
        ],
    },
    entry_points={
        "microcosm.factories": [
            "hello_world = microcosm.example:create_hello_world",
            "opaque = microcosm.opaque:configure_opaque",
        ],
    },
)
