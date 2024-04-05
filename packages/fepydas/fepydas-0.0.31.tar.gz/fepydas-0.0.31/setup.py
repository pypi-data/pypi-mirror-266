#!/usr/bin/python3
from setuptools import setup, find_packages
import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README").read_text()
setup(
  name = "fepydas",
  version = "0.0.31",
  author = "Felix Nippert",
  author_email = "felix@physik.tu-berlin.de",
  description="felix' python data analysis suite",
  long_description=README,
  long_description_content_type="text/markdown",
  url="https://git.tu-berlin.de/nippert/fepydas",
  packages = find_packages(),
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 3',
  ],
  install_requires=['numpy','scipy','lmfit','matplotlib','scikit-learn', 'pyamg'],
  python_requires='>=3',
)
