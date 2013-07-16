import marshal
import struct
import imp
import stat

__author__ = 'matth'
import sys
import os
import py2exe
from py2exe.build_exe import py2exe as build_exe
from py2exe.build_exe import FixupTargets, ensure_unicode, python_dll, RT_BITMAP, RT_MANIFEST
from distutils.dist import Distribution

SCRIPTS = ['warden', 'warden-init', 'warden-install']

class my_py2exe(build_exe):
    def get_boot_script(self, boot_type):
        if boot_type == 'common':

            return os.path.join(os.path.dirname(__file__),
                                "boot_" + boot_type + ".py")
        return super(my_py2exe, self).get_boot_script(boot_type)

    def build_exes(self):
        self.dist_dir = os.path.abspath(sys.prefix)
        self.lib_dir = self.dist_dir
        self.distribution.zipfile = 'Dummy'
        self.bundle_files =  3
        self.skip_archive = True
        arcname = '.'
        for target in FixupTargets([{
                                       'script': os.path.join(self.dist_dir, 'Scripts', '%s-script.py' % s),
                                        'dest_base': s
                                    } for s in SCRIPTS], 'script'):

            dst = self.build_executable(target, self.get_console_template(),
                                    arcname, target.script)
            print dst



    def build_executable(self, target, template, arcname, script, vars={}):
        # Build an executable for the target
        # template is the exe-stub to use, and arcname is the zipfile
        # containing the python modules.
        from py2exe.py2exe_util import add_resource, add_icon
        ext = os.path.splitext(template)[1]
        exe_base = target.get_dest_base()
        exe_path = os.path.join(self.dist_dir, exe_base + ext)
        # The user may specify a sub-directory for the exe - that's fine, we
        # just specify the parent directory for the .zip
        parent_levels = len(os.path.normpath(exe_base).split(os.sep))-1
        lib_leaf = self.lib_dir[len(self.dist_dir)+1:]
        relative_arcname = ((".." + os.sep) * parent_levels)
        if lib_leaf: relative_arcname += lib_leaf + os.sep
        relative_arcname += os.path.basename(arcname)

        src = os.path.join(os.path.dirname(py2exe.build_exe.__file__), template)
        # We want to force the creation of this file, as otherwise distutils
        # will see the earlier time of our 'template' file versus the later
        # time of our modified template file, and consider our old file OK.
        old_force = self.force
        self.force = True
        self.copy_file(src, exe_path, preserve_mode=0)
        self.force = old_force

        # Make sure the file is writeable...
        os.chmod(exe_path, stat.S_IREAD | stat.S_IWRITE)
        try:
            f = open(exe_path, "a+b")
            f.close()
        except IOError, why:
            print "WARNING: File %s could not be opened - %s" % (exe_path, why)

        # We create a list of code objects, and write it as a marshaled
        # stream.  The framework code then just exec's these in order.
        # First is our common boot script.
        boot = self.get_boot_script("common")
        boot_code = compile(file(boot, "U").read(),
                            os.path.abspath(boot), "exec")
        code_objects = [boot_code]
        if self.bundle_files < 3:
            code_objects.append(
                compile("import zipextimporter; zipextimporter.install()",
                        "<install zipextimporter>", "exec"))
        for var_name, var_val in vars.items():
            code_objects.append(
                compile("%s=%r\n" % (var_name, var_val), var_name, "exec")
            )
        if self.custom_boot_script:
            code_object = compile(file(self.custom_boot_script, "U").read() + "\n",
                                  os.path.abspath(self.custom_boot_script), "exec")
            code_objects.append(code_object)
        if script:
            code_object = compile(open(script, "U").read() + "\n",
                                  os.path.basename(script), "exec")
            code_objects.append(code_object)
        code_bytes = marshal.dumps(code_objects)

        if self.distribution.zipfile is None:
            relative_arcname = ""

        si = struct.pack("iiii",
                         0x78563412, # a magic value,
                         self.optimize,
                         self.unbuffered,
                         len(code_bytes),
                         ) + relative_arcname + "\000"

        script_bytes = si + code_bytes + '\000\000'
        self.announce("add script resource, %d bytes" % len(script_bytes))
        if not self.dry_run:
            add_resource(ensure_unicode(exe_path), script_bytes, u"PYTHONSCRIPT", 1, True)

            # add the pythondll as resource, and delete in self.exe_dir
            if self.bundle_files < 2 and self.distribution.zipfile is None:
                # bundle pythonxy.dll
                dll_path = os.path.join(self.bundle_dir, python_dll)
                bytes = open(dll_path, "rb").read()
                # image, bytes, lpName, lpType

                print "Adding %s as resource to %s" % (python_dll, exe_path)
                add_resource(ensure_unicode(exe_path), bytes,
                             # for some reason, the 3. argument MUST BE UPPER CASE,
                             # otherwise the resource will not be found.
                             ensure_unicode(python_dll).upper(), 1, False)

            if self.compressed and self.bundle_files < 3 and self.distribution.zipfile is None:
                zlib_file = imp.find_module("zlib")[0]
                if zlib_file:
                    print "Adding zlib.pyd as resource to %s" % exe_path
                    zlib_bytes = zlib_file.read()
                    add_resource(ensure_unicode(exe_path), zlib_bytes,
                                 # for some reason, the 3. argument MUST BE UPPER CASE,
                                 # otherwise the resource will not be found.
                                 u"ZLIB.PYD", 1, False)

        # Handle all resources specified by the target
        bitmap_resources = getattr(target, "bitmap_resources", [])
        for bmp_id, bmp_filename in bitmap_resources:
            bmp_data = open(bmp_filename, "rb").read()
            # skip the 14 byte bitmap header.
            if not self.dry_run:
                add_resource(ensure_unicode(exe_path), bmp_data[14:], RT_BITMAP, bmp_id, False)
        icon_resources = getattr(target, "icon_resources", [])
        for ico_id, ico_filename in icon_resources:
            if not self.dry_run:
                add_icon(ensure_unicode(exe_path), ensure_unicode(ico_filename), ico_id)

        # a manifest
        mfest, mfest_id = self.build_manifest(target, src)
        if mfest:
            self.announce("add manifest, %d bytes" % len(mfest))
            if not self.dry_run:
                add_resource(ensure_unicode(exe_path), mfest, RT_MANIFEST, mfest_id, False)

        for res_type, res_id, data in getattr(target, "other_resources", []):
            if not self.dry_run:
                if isinstance(res_type, basestring):
                    res_type = ensure_unicode(res_type)
                add_resource(ensure_unicode(exe_path), data, res_type, res_id, False)

        typelib = getattr(target, "typelib", None)
        if typelib is not None:
            data = open(typelib, "rb").read()
            add_resource(ensure_unicode(exe_path), data, u"TYPELIB", 1, False)

        self.add_versioninfo(target, exe_path)

        # Hm, this doesn't make sense with normal executables, which are
        # already small (around 20 kB).
        #
        # But it would make sense with static build pythons, but not
        # if the zipfile is appended to the exe - it will be too slow
        # then (although it is a wonder it works at all in this case).
        #
        # Maybe it would be faster to use the frozen modules machanism
        # instead of the zip-import?
        ##        if self.compressed:
        ##            import gc
        ##            gc.collect() # to close all open files!
        ##            os.system("upx -9 %s" % exe_path)

        if self.distribution.zipfile is None:
            zip_data = open(arcname, "rb").read()
            open(exe_path, "a+b").write(zip_data)

        return exe_path

my_py2exe(Distribution()).build_exes()