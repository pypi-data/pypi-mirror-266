# Always prefer setuptools over distutils
from setuptools import setup, find_packages

company = "google-research--pydemos"
name = "vit_jax"
version = "0.0.2"

from setuptools import setup

setup(
    name=name,
    version=version,
    author="Kotko Vladyslav",
    author_email="m@kotko.org",
    description="",
    packages=find_packages(),
    install_requires=['requests'],
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        ]
)

