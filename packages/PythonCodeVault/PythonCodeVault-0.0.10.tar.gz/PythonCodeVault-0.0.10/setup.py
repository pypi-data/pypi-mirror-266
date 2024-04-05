from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.10'   # https://github.com/fischi1611/CodeVault/blob/main/Coding/Python/PyPI/Publish_Package.md
DESCRIPTION = 'My Python Functions'
LONG_DESCRIPTION = 'My Python Functions - long Description'

# Setting up
setup(
    name="PythonCodeVault",
    version=VERSION,
    author="Kevin Fischer",
    author_email="<kevinfischer1611@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['tqdm'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)