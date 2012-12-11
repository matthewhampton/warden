#!/usr/bin/env python

from glob import glob
from setuptools import find_packages
from distutils.core import setup
setup_kwargs = dict()

install_requires = [
    'sentry>=5.0.21',
    'graphite-web>=0.9.10',
    'CherryPy>=3.2.2'
]

setup(
    name='gentry',
    version='0.0.1',
    url='https://github.com/Supy/gentry',
    author='StJames Software',
    author_email='richardg@sjsoft.com',
    license='Apache Software License 2.0',
    description='A conjoin of Sentry and graphite-web.',
    package_dir={'' : 'src'},
    packages=find_packages('src'),
    scripts=glob('bin/*'),
    install_requires=install_requires,
    **setup_kwargs
)