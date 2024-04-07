"""copyright (c) 2014 - 2024 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""

import os

import setuptools

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name="beeflow-ajax",
    version="1.0.9",
    author="Rafal Przetakowski",
    author_email="office@beeflow.co.uk",
    description="Library to maintain ajax and websockets communication without writing complicated code in JS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/beeflow/BeeflowAjaxPy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
