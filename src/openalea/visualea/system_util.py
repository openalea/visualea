'''
2025-05-23 function copied from openalea.deploy, only used by openalea.deploy and openalea.visualea
Check system configuration and return environment variables dictionary
'''

import pkg_resources
import os
import sys
from os.path import join
from distutils.sysconfig import get_python_lib

# Precedence
INSTALL_DIST = [pkg_resources.EGG_DIST,
                pkg_resources.BINARY_DIST,
                pkg_resources.SOURCE_DIST,
                pkg_resources.CHECKOUT_DIST, ]

DEV_DIST = [pkg_resources.DEVELOP_DIST]
ALL_DIST = DEV_DIST + INSTALL_DIST

def conda_prefix():
    """ Return the conda prefix

    The prefix is the path where libs, bins and includes need to be installed.
    Use this function only in a conda environment (is_conda_env() is True)
    """
    if 'CONDA_BUILD' in os.environ:
        prefix = os.environ['PREFIX']
    else:
        prefix = os.environ['CONDA_PREFIX']

    return os.path.abspath(prefix)

def get_conda_dyn_lib():
    """ Return the path for dynamic library in conda environment """
    env_dir = conda_prefix()
    if ("posix" in os.name):
        dyn_dir = os.path.join(env_dir, 'lib')
    else : # Windows
        dyn_dir = os.path.join(env_dir, 'Library', 'lib')
    return dyn_dir

def get_default_dyn_lib():
    """Return the default path for dynamic library.
       2025-05-23 copied from openalea.deploy
    """
    basedir = get_python_lib()

    # Virtual environment
    if (is_virtual_env()):
        if ("posix" in os.name):
            return os.path.abspath(
                os.path.join(basedir, '../../lib'))
        else:
            return os.path.join(basedir, "shared_libs")

    # Conda environment
    if is_conda_env():
        return get_conda_dyn_lib()

    # Standard environment
    if ("posix" in os.name):
        return "/usr/local/lib"
    else:
        basedir = get_python_lib()
        return os.path.join(basedir, "shared_libs")

def get_dyn_lib_dir(use_default=True):
    """
    Return the shared lib directory
    if use_default : return default directory if not defined
    """
    if is_conda_env():
        return get_default_dyn_lib()

    bdir = get_base_dir("openalea.deploy")
    up_dir = os.path.abspath(join(bdir, os.path.pardir))

    try:
        f = open(join(up_dir, "shared-lib.pth"), 'r')
        lib_dir = f.read()
        print('Reading shared-lib.pth found in %s' % lib_dir)
        f.close()

    except Exception:

        if (use_default):
            lib_dir = get_default_dyn_lib()
        else:
            lib_dir = None

    return lib_dir

def get_base_dir(pkg_name):
    """Return the base directory of a pkg."""
    return pkg_resources.get_distribution(pkg_name).location

def is_virtual_env():
    """ Return True if we are in a virtual env"""

    import site
    return hasattr(site, "virtual_addsitepackages")

def is_conda_env():
    """ Return True if we are in a conda env

    The CONDA_PREFIX environment variable is set by the activate conda script.
    """

    return ('CONDA_PREFIX' in os.environ)

def get_all_bin_dirs(namespace=None, precedence=ALL_DIST):
    """
    Return the iterator of the directories corresponding to the shared lib
    Select only egg with a particular precedence
    """

    egg_names = get_eggs(namespace, precedence)
    for e in egg_names:

        location = get_base_dir(e)

        for sh in get_bin_dirs(e):
            if (os.path.isabs(sh)):
                full_location = sh
            else:
                full_location = join(location, sh)
            yield os.path.normpath(full_location)

def get_bin_dirs(pkg_name):
    """Return a generator which lists the shared lib directory."""
    return get_egg_info(pkg_name, 'bin_dirs.txt')

def get_egg_info(pkg_name, info_key):
    """Return as a generator the egg-infos contained in info_key."""
    dist = pkg_resources.get_distribution(pkg_name)
    try:
        lstr = dist.get_metadata(info_key)
    except:
        lstr = ""

    return pkg_resources.yield_lines(lstr)

def get_eggs(namespace=None, precedence=ALL_DIST):
    """Return as a generator the list of the name of all EGGS in
    a particular namespace (optional)
    select only egg with a particular precedence
    """
    env = pkg_resources.Environment()

    for project_name in env:

        if (precedence):
            pkg = pkg_resources.get_distribution(project_name)
            if (pkg.precedence not in precedence):
                continue

        if (namespace and namespace + '.' in project_name):
            yield project_name

        elif (not namespace):
            yield project_name

def merge_uniq(list1, list2):
    """
    Merge two lists into one with only uniq elements.
    """

    full_list = list(list1)
    full_list.extend([elt for elt in list2 if elt not in list1])
    return full_list

def check_system():
    """
    Check system configuration and

    Return a dictionnary containing environment variables to be set.
    """

    in_env = dict(os.environ)
    out_env = {}

    try:
        if is_virtual_env() or is_conda_env():
            return out_env

        # Linux
        if ("posix" in os.name) and ("linux" in sys.platform.lower()):

            paths = list(get_all_bin_dirs())
            paths = merge_uniq(paths, in_env['PATH'].split(':'))

            libs = [get_dyn_lib_dir()]
            libs = merge_uniq(libs, in_env['LD_LIBRARY_PATH'].split(':'))

            # update the environment
            out_env['LD_LIBRARY_PATH'] = ':'.join(libs)
            out_env['PATH'] = ':'.join(paths)

        # Windows
        elif sys.platform.lower().startswith('win'):

            bin = [d.lower() for d in get_all_bin_dirs()]
            lib = get_dyn_lib_dir().lower()
            if lib not in bin:
                bin.append(lib)

            paths = [d.lower() for d in in_env['PATH'].split(';')]
            libs = merge_uniq(bin, paths)

            out_env['PATH'] = ';'.join(libs)
        # Mac
        elif "darwin" in sys.platform.lower():

            paths = list(get_all_bin_dirs())
            paths = merge_uniq(paths, in_env['PATH'].split(':'))

            libs = [get_dyn_lib_dir()]

            # The environment variable ("DYLD_FRAMEWORK_PATH") is not set with the sudo commands.
            # If "DYLD_LIBRARY_PATH" is in os.environ, we try to run the merge
            try:
                libs = merge_uniq(libs,
                                  in_env['DYLD_FRAMEWORK_PATH'].split(':'))
                libs = merge_uniq(libs, in_env['DYLD_LIBRARY_PATH'].split(':'))

            except:
                pass

            # update the environment
            out_env['DYLD_LIBRARY_PATH'] = ':'.join(libs)
            out_env['DYLD_FRAMEWORK_PATH'] = ':'.join(libs)
            out_env['PATH'] = ':'.join(paths)


    except Exception as e:
        print (e)

    return out_env