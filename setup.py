import os

from setuptools import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="vizydrop-sdk",
    version='0.1.0',
    author="Jonathan Enzinna",
    author_email="jonathan@vizydrop.com",
    description="Vizydrop 3rd Party Application Python SDK - Get visual",
    license="MIT",
    keywords="sdk visualization vizydrop",
    url="https://github.com/vizydrop/vizydrop-python-sdk",
    packages=['vizydrop'],
    long_description=read('README.rst'),
    install_requires=['tornado', 'oauthlib'],
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
