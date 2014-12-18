import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "p0f",
    version = "1.0.0",
    author = "Olli Jarva",
    author_email = "olli@jarva.fi",
    description = ("API client for p0f3"),
    license = "MIT",
    keywords = "p0f fingerprinting API client",
    url = "https://github.com/ojarva/p0f3-api-py",
    packages=['p0f'],
    long_description=read('README.rst'),
    download_url = "https://github.com/ojarva/p0f3-api-py",
    bugtracker_url = "https://github.com/ojarva/p0f3-api-py/issues",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: MIT License",
    ],
)
