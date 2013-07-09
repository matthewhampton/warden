"""
AFTER A NEW INSTALL OF WARDEN (using setup.py) we need to get the system ready for use
1) Make sure warden.settings exists
2) read warden.settings file (or use command line parameters, arguments etc)
3) carbon: ensure the required configuration files are present
4) diamond: ensure the required configuration files are present
5) gentry:  read settings module
            check if database exists... clear...syncdb...migrate etc..
"""
import getpass
from warden.AutoConf import autoconf
from warden_logging import log
import os
import sys
import imp
import base64
import textwrap
import re
from django.core import management
from distutils import dir_util, file_util


def setup(
        home,
        super_user,
        project_name
):
    """
    Warden uses values from its default settings file UNLESS explicitely defined
    here in the constructor.
    """
    os.environ['DJANGO_SETTINGS_MODULE'] = 'gentry.settings'

    log.info ('$DJANGO_SETTINGS_MODULE = %s' % os.environ['DJANGO_SETTINGS_MODULE'])
    from django.conf import settings as gsetts

    database = gsetts.DATABASES['default']['NAME']

    if not os.path.exists(os.path.dirname(database)):
        os.makedirs(os.path.dirname(database))

    management.execute_from_command_line(['manage.py', 'syncdb','--noinput'])
    management.execute_from_command_line(['manage.py', 'migrate', '--noinput'])

    # add a super user
    if super_user:
        username = super_user[0]
        password = super_user[1]
        email = super_user[2]

        from sentry.models import User
        try:
            auser = User.objects.using('default').get(username=username)
        except User.DoesNotExist:
            auser = User.objects.db_manager('default').create_superuser(username, email, password)
            log.info('Added Sentry superuser "%s" with password like "%s%s"' % (username, password[:3], '*'*(len(password)-3)))
        else:
            log.error('Username "%s" is already taken.' % username)

    if project_name:

        project_slug = project_name.lower().replace(' ','_')
        try:
            # add a project
            from sentry.models import Project, Team
            team = Team.objects.create(name=project_name + ' Team', slug=project_slug + '_team', owner=auser)
            project = Project.objects.create(name=project_name, slug=project_slug, owner=auser, team=team)
            key = project.key_set.filter(user=auser)[0]
            dsn = "http://%s:%s@localhost:%s/%s" % (key.public_key, key.secret_key, gsetts.SENTRY_WEB_PORT, key.project_id)
            log.info('Added "%s" project to Sentry with dsn: %s' % (project_name, dsn))

        except Exception:
            log.error('Failed to create project.')

def indent(text, spaces=4, strip=False):
    """
    Borrowed from fabric

    Return ``text`` indented by the given number of spaces.

    If text is not a string, it is assumed to be a list of lines and will be
    joined by ``\\n`` prior to indenting.

    When ``strip`` is ``True``, a minimum amount of whitespace is removed from
    the left-hand side of the given string (so that relative indents are
    preserved, but otherwise things are left-stripped). This allows you to
    effectively "normalize" any previous indentation for some inputs.
    """
    # Normalize list of strings into a string for dedenting. "list" here means
    # "not a string" meaning "doesn't have splitlines". Meh.
    if not hasattr(text, 'splitlines'):
        text = '\n'.join(text)
        # Dedent if requested
    if strip:
        text = textwrap.dedent(text)
    prefix = ' ' * spaces
    output = '\n'.join(prefix + line for line in text.splitlines())
    # Strip out empty lines before/aft
    output = output.strip()
    # Reintroduce first indent (which just got stripped out)
    output = prefix + output
    return output

def passprompt(prompt_str):
    p1 = getpass.getpass(prompt_str)
    p2 = getpass.getpass('(Again!) ' + prompt_str)
    while p1 != p2:
        p1 = getpass.getpass('(Um. They didn\'t match) ' + prompt_str)
        p2 = getpass.getpass('(Again!) ' + prompt_str)
    return p1

def prompt(text, default='', validate=None, password=False):
    """
    Borrowed from fabric!

    Prompt user with ``text`` and return the input (like ``raw_input``).

    A single space character will be appended for convenience, but nothing
    else. Thus, you may want to end your prompt text with a question mark or a
    colon, e.g. ``prompt("What hostname?")``.

    If ``default`` is given, it is displayed in square brackets and used if the
    user enters nothing (i.e. presses Enter without entering any text).
    ``default`` defaults to the empty string. If non-empty, a space will be
    appended, so that a call such as ``prompt("What hostname?",
    default="foo")`` would result in a prompt of ``What hostname? [foo]`` (with
    a trailing space after the ``[foo]``.)

    The optional keyword argument ``validate`` may be a callable or a string:

    * If a callable, it is called with the user's input, and should return the
      value to be stored on success. On failure, it should raise an exception
      with an exception message, which will be printed to the user.
    * If a string, the value passed to ``validate`` is used as a regular
      expression. It is thus recommended to use raw strings in this case. Note
      that the regular expression, if it is not fully matching (bounded by
      ``^`` and ``$``) it will be made so. In other words, the input must fully
      match the regex.

    Either way, `prompt` will re-prompt until validation passes (or the user
    hits ``Ctrl-C``).

    .. note::
        `~fabric.operations.prompt` honors :ref:`env.abort_on_prompts
        <abort-on-prompts>` and will call `~fabric.utils.abort` instead of
        prompting if that flag is set to ``True``. If you want to block on user
        input regardless, try wrapping with
        `~fabric.context_managers.settings`.

    Examples::

        # Simplest form:
        environment = prompt('Please specify target environment: ')

        # With default, and storing as env.dish:
        prompt('Specify favorite dish: ', 'dish', default='spam & eggs')

        # With validation, i.e. requiring integer input:
        prompt('Please specify process nice level: ', key='nice', validate=int)

        # With validation against a regular expression:
        release = prompt('Please supply a release name',
                validate=r'^\w+-\d+(\.\d+)?$')

        # Prompt regardless of the global abort-on-prompts setting:
        with settings(abort_on_prompts=False):
            prompt('I seriously need an answer on this! ')

    """
    default_str = ""
    if default != '':
        default_str = " [%s] " % str(default).strip()
    else:
        default_str = " "
        # Construct full prompt string
    prompt_str = text.strip() + default_str
    # Loop until we pass validation
    value = None
    while value is None:
        # Get input
        value = (passprompt(prompt_str) if password else raw_input(prompt_str)) or default
        # Handle validation
        if validate:
            # Callable
            if callable(validate):
                # Callable validate() must raise an exception if validation
                # fails.
                try:
                    value = validate(value)
                except Exception, e:
                    # Reset value so we stay in the loop
                    value = None
                    print("Validation failed for the following reason:")
                    print(indent(e.message) + "\n")
            # String / regex must match and will be empty if validation fails.
            else:
                # Need to transform regex into full-matching one if it's not.
                if not validate.startswith('^'):
                    validate = r'^' + validate
                if not validate.endswith('$'):
                    validate += r'$'
                result = re.findall(validate, value)
                if not result:
                    print("Regular expression validation failed: '%s' does not match '%s'\n" % (value, validate))
                    # Reset value so we stay in the loop
                    value = None
    return value

def main():
    import argparse
    import ConfigParser
    parser = argparse.ArgumentParser(description='Warden init script')
    parser.add_argument('home', nargs=1, help="the warden home folder")

    prompt_args = [
        ('first-project', "the first sentry project", 'first_project'),
        ('super-user', "the user name for the admin user", 'super_user'),
        ('super-password', "the password for the admin user", 'super_password'),
        ('super-email', "the email address for the admin user", 'super_email'),
    ]

    for arg,help,dest in prompt_args:
        parser.add_argument('--%s' % arg, help=help, dest=dest, required=False)

    args = parser.parse_args()

    for arg,help,dest in prompt_args:
        if not getattr(args, dest, None):
            setattr(args, dest, prompt('Enter %s:' % (help), password='password' in arg))

    home = args.home[0]
    home = os.path.abspath(os.path.expanduser(home))
    os.environ['WARDEN_HOME'] = home

    dir_util.copy_tree(os.path.join(os.path.dirname(__file__), 'templateconf'), home)

    autoconf(home)

    suser = (args.super_user, args.super_password, args.super_email)

    setup(home, suser, args.first_project)

if __name__ == '__main__':
    main()
