# setup.py

import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="factorslib",
    version="5.4",
    author="wytxty",
    author_email="yvettewkkaa@gmail.com",
    description="financial factors calculation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wytxty/factorslib",
    packages=setuptools.find_packages(),
    license="MIT")
