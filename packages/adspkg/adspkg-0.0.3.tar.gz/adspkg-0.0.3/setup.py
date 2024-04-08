from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.3'
DESCRIPTION = 'basic hello pkg'

# Setting up
setup(
    name="adspkg",
    version=VERSION,
    author="Mathew Patil",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)