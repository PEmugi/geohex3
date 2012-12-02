from setuptools import setup, find_packages
import os

from geohex import __version__ as VERSION

long_description = open("README.rst").read()

entry_points = {
    'console_scripts': [
        'gen_hex = geohex.tools:gen_hex'
        ]
        }

setup(name="geohex",
    version=VERSION,
    description="GEOHEX V3 Library",
    long_description=long_description,
    keywords='',
    author="Shimpei Matsuura",
    author_email="PEmugi@me.com",
    url="http://www.chizuwota.net",
    packages=find_packages(exclude=["ez_setup"]),
    install_requires=["setuptools"],
    tests_require=["nose"],
    test_suite = "nose.collector",
    entry_points = entry_points
    )
