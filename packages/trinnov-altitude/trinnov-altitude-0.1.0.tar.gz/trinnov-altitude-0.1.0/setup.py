"""This module provides setup for pip."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="trinnov-altitude",
    version="0.1.0",
    url="https://github.com/binarylogic/py-trinnov-altitude",
    license="Apache 2.0",
    author="Ben Johnson",
    author_email="ben@binarylogic.com",
    description="Python client for interfacing with the Trinnov Altitude processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Home Automation",
    ],
)
