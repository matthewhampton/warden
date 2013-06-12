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

def merge_conf(conf_path, conf_section):
    if not os.path.exists(conf_path):
        file_util.copy_file(conf_path + '.example', conf_path)
    conf = ConfigObj(conf_path)
    merge(conf, conf_section)
    conf.write()

def autoconf(home):
    warden_configuration_file = os.path.join(home, 'warden.config')

    if not os.path.exists(warden_configuration_file):
        file_util.copy_file(warden_configuration_file + '.example', warden_configuration_file)

    config = ConfigObj(warden_configuration_file)

    if not 'gentry' in config:
        config['gentry'] = {}

    if not 'sentry_key' in config['gentry']:
        config['gentry']['sentry_key'] = base64.b64encode(os.urandom(40))

    config.write()

    for section in config:
        if section == 'diamond.conf':
            conf_path = os.path.abspath(os.path.join(home, 'diamond', section))
            merge_conf(conf_path, config[section])

        elif section.endswith('.conf'):
            conf_path = os.path.abspath(os.path.join(home, 'graphite', 'conf', section))
            merge_conf(conf_path, config[section])

    gentry_settings = os.path.abspath(os.path.join(home, 'gentry_settings.py'))
    if os.path.exists(gentry_settings):
        os.remove(gentry_settings)

    file_util.copy_file(gentry_settings + '.example', gentry_settings)

    # write key into settings file
    try:
        with open(gentry_settings) as f:
            old_lines = f.readlines()
        rewrite = False
        new_lines = []
        for line in old_lines:
            if line.startswith('__SENTRY_KEY__'):
                nline = 'SENTRY_KEY=\'' + str(config['gentry']['sentry_key']) + '\'\n'
                rewrite = True
                log.info( 'Rewriting "%s" -> "%s"' % (line.strip(), nline.strip()))
            else:
                nline = line
            new_lines.append(nline)
        if rewrite:
            log.info('Writing new Sentry_key into settings module "%s"' % gentry_settings)
            with open(gentry_settings, 'w') as f:
                f.writelines(new_lines)
                f.flush()
                f.close()
    except IOError:
        log.exception('Could not write gentry_settings module: "%s"' % gentry_settings)



def main():
    import argparse
    parser = argparse.ArgumentParser(description='Warden auto conf script')
    parser.add_argument('home', nargs=1, help="the warden home folder")
    args = parser.parse_args()
    autoconf(args.home[0])

if __name__ == '__main__':
    main()
