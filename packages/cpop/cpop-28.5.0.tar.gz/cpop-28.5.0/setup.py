import os

from Cython.Build import cythonize
from setuptools import Extension
from setuptools import setup

extensions = [
    Extension("pop.data", [os.path.join("pop", "pop.data.pyx")]),
    Extension("pop.contract", [os.path.join("pop", "pop.contract.pyx")]),
]

setup(
    ext_modules=cythonize(extensions),
)
