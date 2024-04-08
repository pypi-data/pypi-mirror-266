#!/usr/bin/env python3

import re

from setuptools import setup

string_equality = re.compile(r"""__([\w_]+)__\s*=\s*"(.+)"$""")

data = {}

with open("owmpy/__init__.py", "r") as file:
    for line in file.readlines():
        if (match := re.match(string_equality, line)) is not None:
            data[match[1]] = match[2]

data.pop("copyright", None)

with open("README.md", "r") as file:
    readme = file.read()

requirements: list[str] = []
with open("requirements.txt", "r") as file:
    for line in file.read().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            requirements.append(line)

setup(
    name=data.pop("title"),
    description="A wrapper for the OpenWeatherMap API",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["owmpy"],
    package_data={"owmpy": ["py.typed"]},
    include_package_data=True,
    **data,  # type: ignore
)
