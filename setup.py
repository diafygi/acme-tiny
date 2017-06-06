from setuptools import setup
import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASE_PATH, "README.md"), "rb") as f:
    long_description = f.read().decode("UTF-8")

setup(
    name="acme-tiny",
    version="2.1", # version number standard: PEP440

    description="A tiny script to issue and renew TLS certs from Let's Encrypt",
    long_description=long_description,

    url="https://github.com/diafygi/acme-tiny",

    author="Daniel Roesler",
    author_email="diafygi@gmail.com",

    license="MIT",

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],

    packages=[],

    install_requires=[],
    extras_require={
        "dev": [],
        "test": ["coveralls", "fusepy", "argparse"],
    },

    scripts=["acme_tiny.py"],

)
