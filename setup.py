from setuptools import setup, find_packages

setup(
    name="bfrpg_mud",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*", "tests", "tests.*"]),
) 