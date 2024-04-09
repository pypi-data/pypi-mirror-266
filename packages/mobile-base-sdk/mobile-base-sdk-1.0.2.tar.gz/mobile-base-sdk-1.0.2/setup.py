#!/usr/bin/env python
"""Setup config file."""

from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="mobile-base-sdk",
    version="1.0.2",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "numpy>=1.24.0,<=1.26.4",
        "grpcio>=1.59.0, <=1.62.2",
        "protobuf>=4.25.0, <=4.25.3",
        "pygame",
        "pillow",
        "reachy2-sdk-api>=1.0.0,<1.1.0",
    ],
    extras_require={
        "doc": ["sphinx"],
    },
    author="Pollen Robotics",
    author_email="contact@pollen-robotics.com",
    url="https://github.com/pollen-robotics/mobile-base-sdk",
    description="Mobile Base SDK for the Reachy robot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
