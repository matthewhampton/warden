import ConfigParser
import base64
import os
from distutils import file_util
from configobj import ConfigObj, Section
from warden_logging import log

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

def get_warden_conf():
    warden_configuration_file = os.path.join(os.environ['WARDEN_HOME'], 'warden.config')

    if not os.path.exists(warden_configuration_file):
        file_util.copy_file(warden_configuration_file + '.example', warden_configuration_file)

    return ConfigObj(warden_configuration_file)

def home_path(*args):
    return os.path.abspath(os.path.join(os.environ['WARDEN_HOME'], *args))

def diamond_conf(wardenconf, conf):
    conf['server']['collectors_path'] = home_path('diamond', 'share', 'diamond', 'collectors')
    conf['server']['collectors_config_path'] = home_path('diamond', 'collectors')
    conf['server']['handlers_config_path'] = home_path('diamond', 'handlers')
    conf['server']['pid_file'] = home_path('diamond', 'diamond.pid')
    conf['handlers']['ArchiveHandler']['log_file'] = home_path('log', 'diamond_archive.log')
    conf['handler_rotated_file']['args'] = (home_path('log', 'diamond.log'), 'midnight', 1, 7)



def autoconf(home):
    os.environ['WARDEN_HOME'] = home

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
    parser.add_argument('home', nargs=1, help="the warden home folder")
    args = parser.parse_args()
    autoconf(args.home[0])

if __name__ == '__main__':
    main()
