import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "SimDataDB",
    version = "0.2",
    author = "Alejandro Francisco Queiruga",
    description = "",
    license = "GPL",
    keywords = "",
    test_suite="test",
    packages=['SimDataDB'],
    long_description=read('Readme.md'),
    classifiers=[],
)
