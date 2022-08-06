from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="testtrading",
    version="0.0.1",
    description="test create a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ronshen0404/tradingsystem",
    author="ronshen0404",
    author_email="ronshen0404@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mysql-connector-python==8.0.30",
        "matplotlib>=3.5.2",
        "numpy>=1.23.1",
        "pandas>=1.4.3",
        "yfinance>=0.1.74"
    ]
)