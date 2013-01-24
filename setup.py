#!/usr/bin/env python

from glob import glob
from setuptools import find_packages
from distutils.core import setup
setup_kwargs = dict()

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
    install_requires=[
        'Django==1.4.2',
        'django-tagging==0.3.1',
        'sentry>=5.0.21',
        'graphite-web==0.9.10-warden',
        'CherryPy>=3.2.2',
        'sentry_jsonmailprocessor',
        ],
    dependency_links=[
        'http://github.com/Supy/sentry_jsonmailprocessor/tarball/master#egg=sentry_jsonmailprocessor-0.0.1',
        'http://github.com/richg/graphite-web/tarball/0.9.x#egg=graphite-web-0.9.10-warden'
        ],
    **setup_kwargs
)
