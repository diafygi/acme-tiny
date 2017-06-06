#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup

long_description = """
acme-tiny is a tiny script to issue and renew TLS certs from Let's Encrypt

This is a tiny, auditable script that you can throw on your server to issue and
renew Let's Encrypt certificates. Since it has to be run on your server and have
access to your private Let's Encrypt account key, I tried to make it as tiny as
possible (currently less than 200 lines). The only prerequisites are python and
openssl.
"""

setup(
    name='acme-tiny',
    version='20151229',

    description="acme-tiny is a tiny script to issue and renew TLS certs from Let's Encrypt",
    long_description=long_description,

    license='MIT',
    url='https://github.com/diafygi/acme-tiny',

    author='Daniel Roesler',
    author_email='diafygi@gmail.com',

    maintainer='Jeremías Casteglione',
    maintainer_email='debian@jrms.com.ar',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='development',
    py_modules=['acme_tiny'],

    entry_points={
        'console_scripts': [
            'acme-tiny=acme_tiny:__entry_point',
        ],
    },
)
