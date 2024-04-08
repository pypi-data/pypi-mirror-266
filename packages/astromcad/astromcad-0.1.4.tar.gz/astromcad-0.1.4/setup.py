from setuptools import setup, find_packages
import codecs
import os

with open("READMEPyPI.md", "r") as fh:
    long_description = fh.read();

VERSION = '0.1.4'
DESCRIPTION = 'Classifier-Based Anomaly Detection for Astronomical Transients'
LONG_DESCRIPTION = long_description

# Setting up
setup(
    name="astromcad",
    version=VERSION,
    author="Rithwik Gupta",
    author_email="<rithwikca2020@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'keras==2.15.0', 'tensorflow==2.15.0', 'matplotlib', 'scikit-learn==1.2.2'],
    keywords=[],
    package_data={'astromcad': ['*.keras', '*.pickle']},
    include_package_data=True,
    
)