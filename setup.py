from setuptools import find_packages, setup

project = "marquez"
version = "0.0.1"

setup(
    name=project,
    version=version,
    description="Marquez - Simple microservice configuration",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="marquez",
    install_requires=[
        "easydict>=1.6",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
