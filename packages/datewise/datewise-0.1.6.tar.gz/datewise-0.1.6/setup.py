from setuptools import setup, find_packages
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="datewise",
    version="0.1.6",
    description="Thesis Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://datewise.readthedocs.io/",
    author="Sebastian Gontkovic",
    author_email="sebascngont@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
    ],
    packages=["datewise"],
    include_package_data=True,
    install_requires=["pandas", "numpy", "python-dateutil", "pytest"]
)
