from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1.3'
DESCRIPTION = 'skdir'
LONG_DESCRIPTION = 'A package to perform 5th sem AIML lab'

# Setting up
setup(
    name="skdir",
    version=VERSION,
    author="Sk",
    author_email="karnamsharath3@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy>=1.21.0',
        'scikit-learn>=0.24.0',
        'matplotlib>=3.4.0',],
    keywords=['arithmetic', 'math', 'mathematics', 'python tutorial', 'avi upadhyay'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)