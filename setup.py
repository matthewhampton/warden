from setuptools import setup
import re
from glob import glob
import os

def get_version():
    VERSIONFILE="src/warden/__init__.py"
    initfile_lines = open(VERSIONFILE, "rt").readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

def check_fault_requires():
    pass

setup(
    name             = 'warden',
    version          = get_version(),
    license          =  'MIT',
    description      = 'A set of tools for monitoring Python applications, and shipping events to Sentry and metrics to Graphite',
    long_description = \
"""
Warden is a Python application that monitors other Python applications running locally, and ships events to a Sentry instance and metrics to a Graphite instance.

Warden uses Diamond to collect stats. Using Diamond's plug-in Collectors architecture, many stats can be collected and custom Collectors added.
""",
    author           = 'Richard Graham',
    author_email     = 'support@sjsoft.com',
    packages         = [
        'warden',
        'warden.smtp_forwarder',
        'warden.installer',
        'gentry',
        'gentry.management',
        'gentry.management.commands'],
    package_dir={'' : 'src'},
    package_data={
        'warden': [os.path.join('templateconf','*.example')],
        'warden.installer': ['warden_requirements*.txt']},
    scripts=glob('bin/*'),
    zip_safe = False,
    #Please refer to src/warden/installer for the dependencies... We need to install them carefully
    install_requires = [],
    keywords         = 'sentry carbon graphite monitoring',
    url              = 'https://github.com/richg/warden',
    entry_points     = {
          'console_scripts': [
              'warden = warden.WardenServer:main',
              'warden-install = warden.installer.Installer:main',
              'warden-init = warden.warden_init:main'
          ]
    },
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Web Environment',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
