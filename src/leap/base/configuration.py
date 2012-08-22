"""
Configuration Base Class
"""

import grp
import logging
import requests
import os

logger = logging.getLogger(name=__name__)
logger.setLevel('DEBUG')


class Configuration(object):
    """
    I have no idea how configuration
    (txt vs. sqlite) will be done, but let's stub it now.
    """
    pass


def get_config_dir():
    """
    get the base dir for all leap config
    @rparam: config path
    @rtype: string
    """
    # TODO
    # check for $XDG_CONFIG_HOME var?
    # get a more sensible path for win/mac
    # kclair: opinion? ^^
    return os.path.expanduser(
                os.path.join('~',
                             '.config',
                             'leap'))


def get_config_file(filename, folder=None):
    """
    concatenates the given filename
    with leap config dir.
    @param filename: name of the file
    @type filename: string
    @rparam: full path to config file
    """
    path = []
    path.append(get_config_dir())
    if folder is not None:
        path.append(folder)
    path.append(filename)
    return os.path.join(*path)


def get_default_provider_path():
    default_subpath = os.path.join("providers",
                                   "default")
    default_provider_path = get_config_file(
        '',
        folder=default_subpath)
    return default_provider_path


def validate_ip(ip_str):
    """
    raises exception if the ip_str is
    not a valid representation of an ip
    """
    socket.inet_aton(ip_str)


def get_username():
    return os.getlogin()


def get_groupname():
    gid = os.getgroups()[-1]
    return grp.getgrgid(gid).gr_name


def get_config_json(config_file=None):
    """
    will replace get_config function be developing them
    in parralel for branch purposes.
    @param: configuration file
    @type: file
    @rparam: configuration turples
    @rtype: dictionary
    """
    if not config_file:
        fpath = get_config_file('eip.json')
        if not os.path.isfile(fpath):
            dpath, cfile = os.path.split(fpath)
            if not os.path.isdir(dpath):
                mkdir_p(dpath)
            with open(fpath, 'wb') as configfile:
                configfile.flush()
        config_file = open(fpath)

    config = json.load(config_file)

    return config


def get_definition_file(url=None):
    """
    """
    #TODO: determine good default location of definition file.
    r = requests.get(url)
    return r.json
