#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for the Tire Impedance Diagnostic System package.
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="tire-impedance-diagnostic",
    version="0.1.0",
    author="Ucaretron Inc.",
    author_email="contact@ucaretron.com",
    description="A simulation of a tire condition diagnostic system using impedance measurement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JJshome/tire-impedance-diagnostic",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tire-diagnostic=tire_diagnostic_system:main",
        ],
    },
)
