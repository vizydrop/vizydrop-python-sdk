import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test
from vizydrop import __version__ as SDK_VERSION

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name="vizydrop-sdk",
    version=SDK_VERSION,
    author="Jonathan Enzinna",
    author_email="jonathan@vizydrop.com",
    description="Vizydrop 3rd Party Application Python SDK - Get visual",
    license="MIT",
    keywords="sdk visualization vizydrop",
    url="https://github.com/vizydrop/vizydrop-python-sdk",
    packages=find_packages(exclude=['tests', 'examples']),
    long_description=read('README.rst'),
    install_requires=['tornado<4.3', 'oauthlib', 'pymongo'],
    tests_require=['pytest', 'toro'],
    cmdclass = {'test': PyTest},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only"
    ],
)
