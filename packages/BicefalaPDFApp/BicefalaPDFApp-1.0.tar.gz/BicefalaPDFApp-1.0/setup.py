"""Important file to publish this package in Pypi"""

from pathlib import Path
import setuptools

setuptools.setup(
    name="BicefalaPDFApp",
    version=1.0,
    long_description=Path("README.md").read_text(encoding="utf-8"),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
