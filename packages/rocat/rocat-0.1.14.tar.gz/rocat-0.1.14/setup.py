# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rocat",
    version="0.1.14",
    description="A simple and user-friendly library for AI services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YumetaLab",
    author_email="root@yumeta.kr",
    url="https://github.com/Yumeta-Lab/rocat",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "openai",
        "anthropic",
        "streamlit",
        "matplotlib"
    ],
    package_data={
        "": ["*.py"],
    },
    include_package_data=True,
)