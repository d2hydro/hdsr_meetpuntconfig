# -*- coding: utf-8 -*-
from setuptools import setup
import pkg_resources  # part of setuptools


from meetpuntconfig import __version__

#%%
with open("README.md", encoding="utf8") as f:
    long_description = f.read()

setup(
    name="meetpuntconfig",
    version=__version__,
    description="to check consistency HDSR meetpuntconfig with FEWS",
    long_description=long_description,
    url="https://github.com/d2hydro/hdsr_meetpuntconfig",
    author="Daniel Tollenaar",
    author_email="daniel@d2hydro.nl",
    license="MIT",
    packages=["meetpuntconfig"],
    python_requires=">=3.6",
    install_requires=[
        "configparser",
        "geopandas",
        "lxml",
        "numpy",
        "openpyxl",
        "pandas>=1.1.0",
        "spyder",
        "xlrd>=1.0.0"
    ],
    keywords="HDSR meetpuntconfig FEWS",
)
