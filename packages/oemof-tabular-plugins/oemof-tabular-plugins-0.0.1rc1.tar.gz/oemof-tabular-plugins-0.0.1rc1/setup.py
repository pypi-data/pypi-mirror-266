"""Only meant to be used for `pip install -e .`"""

from setuptools import setup, find_packages, Extension

setup_args = dict(
    packages=find_packages(where="src"),  # list
    package_dir={"": "src"},  # mapping
)

setup(**setup_args)
