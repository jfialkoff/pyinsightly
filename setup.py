import sys

from setuptools import setup, find_packages

install_requires = [
    'requests >= 2.5',
]

setup(
    name = "pyinsightly",
    version = '0.1',
    description = "Insightly Python SDK",
    url = "https://github.com/jfialkoff/pyinsightly",
    author = "Joshua Fialkoff",
    author_email = "josh@goodotter.com",
    packages = find_packages(),
    install_requires = install_requires,
)
