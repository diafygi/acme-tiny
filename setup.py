from setuptools import setup

VERSION = '0.0.1'

DISTNAME = 'acme_tiny'
LICENSE = 'MIT'
MAINTAINER = "Daniel Roesler"
EMAIL = "None"
URL = "None"
DESCRIPTION = "None"
LONG_DESCRIPTION = "None"

SCRIPTS = ['scripts/acme_tiny']

setup(
    name=DISTNAME,
    version=VERSION,
    scripts=SCRIPTS,
    license=LICENSE,
    url=URL,
    maintainer_email=EMAIL,
    maintainer=MAINTAINER,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION)
