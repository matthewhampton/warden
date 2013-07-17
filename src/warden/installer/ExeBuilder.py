import marshal
import struct
import imp
import stat

__author__ = 'matth'
import sys
import os
import py2exe
from py2exe.build_exe import py2exe as build_exe
from py2exe.build_exe import FixupTargets, Target, ensure_unicode, python_dll, RT_BITMAP, RT_MANIFEST

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
    def get_boot_script(self, boot_type):
        if boot_type == 'common':

            return os.path.join(os.path.dirname(__file__),
                                "boot_" + boot_type + ".py")
        return build_exe.get_boot_script(self, boot_type)

    def build_exes(self, scripts_dir, dest_dir):
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

if __name__ == '__main__':
    from distutils.dist import Distribution
    dest_dir = sys.prefix
    scripts_dir = os.path.join(dest_dir, 'Scripts')
    my_py2exe(Distribution()).build_exes(scripts_dir, dest_dir)