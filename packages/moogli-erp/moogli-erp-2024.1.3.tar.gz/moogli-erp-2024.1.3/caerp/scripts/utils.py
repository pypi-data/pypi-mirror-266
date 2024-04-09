"""
    script utility, allows the use of the app's context (database, models ...)
    from within command line calls
"""
import logging
import sys
from argparse import ArgumentParser

from docopt import docopt
from pyramid.paster import bootstrap
from transaction import commit
from pyramid.paster import setup_logging
from caerp.utils import ascii


def command(func, doc):
    """
    Usefull function to wrap command line scripts using docopt lib

    /!\ if starting to use this commande, you may want to use argparse_command() instead.
    (docopt is deprecated).

    If at any time, this commande becomes unused, remove it, and remove docopt
    from requirements.
    """
    logging.basicConfig()
    args = docopt(doc)
    pyramid_env = bootstrap(args["<config_uri>"])
    setup_logging(args["<config_uri>"])
    try:
        func(args, pyramid_env)
    finally:
        pyramid_env["closer"]()
    commit()
    return 0


def argparse_command(func, argparser: ArgumentParser, pyramid_env=None):
    """
    Wrap command line scripts, using argparse builtin module
    """
    logging.basicConfig()
    args = argparser.parse_args(sys.argv[1:])
    # L'app pyramid peut être bootstrappée avant dans le cas d'caerp-admin
    # par exemple
    if pyramid_env is None:
        pyramid_env = bootstrap(args.config_uri)
    setup_logging(args.config_uri)
    try:
        func(args, pyramid_env)
    finally:
        pyramid_env["closer"]()
    commit()
    return 0


def get_argument_value(arguments, key, default=None):
    """
    Return the value for an argument named key in arguments or default

    :param dict arguments: The cmd line arguments returned by docopt
    :param str key: The key we look for (type => --type)
    :param str default: The default value (default None)

    :returns: The value or default
    :rtype: str
    """
    val = arguments.get("<%s>" % key)
    if not val:
        val = default

    return ascii.force_unicode(val)


def get_value(arguments, key, default=None):
    """
    Return the value of an option named key in arguments or default

    :param dict arguments: The cmd line arguments returned by docopt
    :param str key: The key we look for (type => --type)
    :param str default: The default value (default None)

    :returns: The value or default
    :rtype: str
    """
    if not key.startswith("--"):
        key = "--%s" % key
    val = arguments.get(key)
    if not val:
        val = default

    return ascii.force_unicode(val)
