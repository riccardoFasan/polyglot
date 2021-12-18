#!/usr/bin/env python3
import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="deeply",
    version="0.0.7",
    description="Automation CLI tool that, using the DeepL API, generates a JSON or a PO file from a given source file.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/riccardoFasan/deepl-translator-script",
    project_urls={
        "BugTracker" : "https://github.com/riccardoFasan/deepl-translator-script/issues",
        "Homepage" : "https://github.com/riccardoFasan/deepl-translator-script"
    },
    author="Riccardo Fasan",
    author_email="fasanriccardo21@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "six>=1.16.0",
        "python-utils>=2.5.6",
        "colorama>=0.4.4",
        "polib>=1.1.1",
        "progressbar2>=3.55",
        "charset-normalizer>=2.0.9",
        "requests>=2.26.0",
        "requests-toolbelt>=0.9.1"
    ],
    entry_points={
        "console_scripts": [
            "deeply=deeply.__main__:translate_or_print_data",
        ]
    },
)
