import ConfigParser
import base64
import os
from distutils import file_util
from configobj import ConfigObj, Section
from warden_logging import log
import sys

def merge(left, right):
    """
    A recursive update - useful for merging config files.
    ConfigObj({'section1': {'option1': 'False', 'subsection': {'more_options': 'False'}}})
    """

    for key, val in right.items():
        if (key in left and isinstance(left[key], dict) and
                isinstance(val, dict)):
            merge(left[key], val)
        elif isinstance(val, Section):
            left[key] = val.dict()
        else:
            left[key] = val

def merge_conf(conf_path, conf_section, wardenconf=None, autoconffunc=None):
    if os.path.exists(conf_path):
        os.remove(conf_path)
    file_util.copy_file(conf_path + '.example', conf_path)
    conf = ConfigObj(conf_path)
    if autoconffunc:
        autoconffunc(wardenconf, conf)
    merge(conf, conf_section)
    conf.write()

def get_warden_conf_file():
    warden_configuration_file = os.path.join(os.environ['WARDEN_HOME'], 'warden.config')

    if not os.path.exists(warden_configuration_file):
        file_util.copy_file(warden_configuration_file + '.example', warden_configuration_file)

    return warden_configuration_file

def get_warden_conf():
    return ConfigObj(get_warden_conf_file())

def home_path(*args):
    return os.path.abspath(os.path.join(os.environ['WARDEN_HOME'], *args))

def diamond_conf(wardenconf, conf):
    conf['server']['collectors_path'] = home_path('diamond', 'share', 'diamond', 'collectors')
    conf['server']['collectors_config_path'] = home_path('diamond', 'collectors')
    conf['server']['handlers_config_path'] = home_path('diamond', 'handlers')
    conf['server']['pid_file'] = home_path('diamond', 'diamond.pid')
    conf['handlers']['ArchiveHandler']['log_file'] = home_path('log', 'diamond_archive.log')
    conf['handler_rotated_file']['args'] = (home_path('log', 'diamond.log'), 'midnight', 1, 7)
    conf['handlers']['GraphiteHandler']['host'] = 'localhost'
    conf['handlers']['GraphiteHandler']['port'] = 2023
    conf['handlers']['GraphitePickleHandler']['host'] = 'localhost'
    conf['handlers']['GraphitePickleHandler']['port'] = 2024

def setenv(home):
    os.environ['WARDEN_HOME'] = home
    os.environ['GRAPHITE_ROOT'] = home_path('graphite')
    os.environ['DIAMOND_ROOT'] = home_path('diamond')

def get_default_home():
    if 'win' in sys.platform:
        program_data = os.environ.get('ALLUSERSPROFILE', None)
        if not program_data:
            raise ValueError('Unable to determine default warden home directory as the %ALLUSERSPROFILE% environment variable is not available.')
        return os.path.join(program_data, 'PythonWarden')
    else:
        return '/srv/warden'

def get_home(homearg):
    return os.path.abspath(os.path.expanduser(homearg)) if homearg else get_default_home()

def autoconf(home):
    setenv(home)

    config = get_warden_conf()

    if not 'gentry' in config:
        config['gentry'] = {}

    if not 'sentry_key' in config['gentry']:
        config['gentry']['sentry_key'] = base64.b64encode(os.urandom(40))

    config.write()

    for section in config:
        if section == 'diamond.conf':
            conf_path = os.path.abspath(os.path.join(home, 'diamond', section))
            merge_conf(conf_path, config[section], config, diamond_conf)

        elif section.endswith('.conf'):
            conf_path = os.path.abspath(os.path.join(home, 'graphite', 'conf', section))
            merge_conf(conf_path, config[section])


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Warden auto conf script')
    parser.add_argument('home', nargs='?', help="the warden home folder")
    args = parser.parse_args()
    autoconf(get_home(args.home))

if __name__ == '__main__':
    main()
