import argparse
import subprocess
import os
import sys
import distutils.sysconfig
import pkg_resources
from pip.req import parse_requirements
from distutils.dist import Distribution

def get_requirements(requirements_path=None):
    requirements_path = requirements_path or os.path.join(os.path.dirname(__file__),
        'warden_requirements_win.txt' if 'win' in sys.platform else 'warden_requirements.txt')
    install_reqs = parse_requirements(requirements_path)
    reqs = dict([(ir.name, ir) for ir in install_reqs])
    return reqs

def _run(command):
    print command
    subprocess.check_call(command)

def installed_version(package_name):
    try:
        d = pkg_resources.get_distribution(package_name)
        return d.version
    except pkg_resources.DistributionNotFound:
        return False

def get_req(requirements, package_name):
    if requirements[package_name].url:
        return '%s#egg=%s' % (requirements[package_name].url, requirements[package_name].req)
    else:
        return str(requirements[package_name].req)


def install_libraries(run=None, pip=None, lib=None, scripts=None, prefix=None, data=None, requirements=None):
    requirements = requirements or get_requirements()
    if not 'PIP_DOWNLOAD_CACHE' in os.environ:
        os.environ['PIP_DOWNLOAD_CACHE'] = 'cache'
    run = run or _run
    pip = pip or 'pip'
    _pipping_easy_install = 'pipping_easy_install'

    if lib is None:
        lib= distutils.sysconfig.get_python_lib()
    if prefix is None:
        prefix=sys.exec_prefix
    if scripts is None:
        scripts=os.path.join(prefix,'Scripts') if 'win' in sys.platform else os.path.join(prefix,'bin')

    data = data or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templateconf')

    def pipping_easy_install(package_name):
        v = installed_version(package_name)
        if not v:
            run([_pipping_easy_install, get_req(requirements, package_name)])
        else:
            print 'Package %s (%s) already installed' % (package_name, v)

    def pip_install(package_name, *args):
        v = installed_version(package_name)
        if not v:
            run([pip, 'install', get_req(requirements, package_name)] + list(args))
        else:
            print 'Package %s (%s) already installed' % (package_name, v)

    if 'win' in sys.platform:

        pip_install('pipping-easy-install')
        pipping_easy_install('Twisted')
        pipping_easy_install('psutil')
        pipping_easy_install('pycairo')
        pipping_easy_install('pywin32')
        pipping_easy_install('zope.interface')
        pipping_easy_install('py2exe')
        import ExeBuilder
        ExeBuilder.my_py2exe(Distribution()).build_exes(scripts, prefix)
    else:
        pip_install('pycairo')
        pip_install("python-daemon")
        pip_install("lockfile")

    pip_install("configobj")

    pip_install("whisper",
         '--install-option=--install-scripts=%s' % scripts,
         '--install-option=--prefix=%s' % prefix,
         '--install-option=--install-lib=%s' % lib,
         '--install-option=--install-data=%s' % (os.path.join(data, 'graphite')))

    pip_install("carbon",
         '--install-option=--install-scripts=%s' % scripts,
         '--install-option=--prefix=%s' % prefix,
         '--install-option=--install-lib=%s' % lib,
         '--install-option=--install-data=%s' % (os.path.join(data, 'graphite')))

    os.environ['DIAMOND_CONFIG_DIR'] = os.path.join(data, 'diamond')
    pip_install("diamond",
         '--install-option=--prefix=%s' % prefix,
         '--install-option=--install-scripts=%s' % scripts,
         '--install-option=--install-lib=%s' % lib,
         '--install-option=--install-data=%s' % (os.path.join(data, 'diamond')))

    pip_install("Django")

    pip_install("graphite-web",
         '--install-option=--install-scripts=%s' % scripts,
         '--install-option=--prefix=%s' % prefix,
         '--install-option=--install-lib=%s' % lib,
         '--install-option=--install-data=%s' % (os.path.join(data, 'graphite')))

    pip_install("CherryPy")

    pip_install("sentry")

    pip_install("sentry-jsonmailprocessor")


def main():
    parser = argparse.ArgumentParser(description='Warden installer')
    args = parser.parse_args()
    install_libraries()

if __name__ == '__main__':
    main()