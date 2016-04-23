from setuptools import setup

setup(
    name="acme-tiny",
    use_scm_version=True,
    url="https://github.com/diafygi/acme-tiny",
    author="Daniel Roesler",
    author_email="diafygi@gmail.com",
    description="A tiny script to issue and renew TLS certs from Let's Encrypt",
    license="MIT",
    py_modules=['acme_tiny'],
    entry_points={'console_scripts': [
        'acme-tiny = acme_tiny:main',
    ]},
    setup_requires=['setuptools_scm'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
