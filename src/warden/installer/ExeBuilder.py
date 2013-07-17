import marshal
import struct
import imp
import stat

__author__ = 'matth'
import sys
import os
from py2exe.build_exe import py2exe as build_exe
from py2exe.build_exe import FixupTargets, Target
import tempfile

SCRIPTS = ['warden', 'warden-init', 'warden-install']
SERVICE = Target(
        # used for the versioninfo resource
        description = "The windows service for the Warden monitoring and metrics framework",
        # what to build. For a service, the module name (not the
        # filename) must be specified!
        modules = ["warden.Win32Service"],
        cmdline_style='custom',
        dest_base = 'warden-svc',
    )


class my_py2exe(build_exe):

    def __init__(self, *args, **kwargs):
        build_exe.__init__(self, *args, **kwargs)
        self._tmp_file_list = []

    def get_boot_script(self, boot_type):
        bootscript = build_exe.get_boot_script(self, boot_type)
        if boot_type == 'common':

            with open(bootscript, 'r') as f:
                src = f.read()

            src = """
# Fix up the system path so that we can run off a normal python install:

import sys

pythonhome = sys.prefix[:-1] if sys.prefix.endswith('\\') else sys.prefix

sys.path = [pythonhome + x for x in [
    '\\python27.zip',
    '\\DLLs',
    '\\lib',
    '\\lib\\plat-win',
    '\\lib\\lib-tk',
    '',
    ]]

import site

""" + src

            (f, name) = tempfile.mkstemp(suffix='wardenboot.py', text=True)
            try:
                f.write(src)
            finally:
                self._tmp_file_list.append(name)
                f.close()


            return name
        return bootscript

    def build_exes(self, scripts_dir, dest_dir):
        try:
            self.dist_dir = dest_dir
            self.lib_dir = self.dist_dir
            self.distribution.zipfile = 'Dummy'
            self.bundle_files = 3
            self.skip_archive = True
            arcname = '.'
            for target in FixupTargets([{
                                           'script': os.path.join(scripts_dir, '%s-script.py' % s),
                                            'dest_base': s
                                        } for s in SCRIPTS], 'script'):

                dst = self.build_executable(target, self.get_console_template(),
                                        arcname, target.script)

            dst = self.build_service(SERVICE, self.get_service_template(),
                                     arcname)
        finally:
            for f in self._tmp_file_list:
                if os.path.exists(f):
                    try:
                        os.unlink(f)
                    except:
                        pass


if __name__ == '__main__':
    from distutils.dist import Distribution
    dest_dir = sys.prefix
    scripts_dir = os.path.join(dest_dir, 'Scripts')
    my_py2exe(Distribution()).build_exes(scripts_dir, dest_dir)