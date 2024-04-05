import codecs
import os

from setuptools import find_packages, setup

# these things are needed for the README.md show on pypi
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '0.1.0'
DESCRIPTION = 'A visual novel framework based on pygame.'
LONG_DESCRIPTION = 'A visual novel framework based on pygame.'

# Setting up
setup(
    name="pyavg",
    version=VERSION,
    author="London Class",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'pygame-ce>=2.4.0',
    ],
    keywords=['python', 'pygame'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ]
)