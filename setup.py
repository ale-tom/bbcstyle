from setuptools import setup, find_packages

setup(
    name="bbcstyle",
    version="1.0",
    packages=find_packages(where="bbcstyle"),
    package_dir={"": "bbcstyle"},
)
