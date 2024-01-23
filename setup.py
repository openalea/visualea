 # -*- coding: utf-8 -*-

import sys
from os.path import join as pj

from setuptools import setup, find_namespace_packages

# find version number in src/openalea/core/version.py
_version = {}
with open("src/openalea/visualea/version.py") as fp:
    exec(fp.read(), _version)
    version = _version["__version__"]

#metadata = read_metainfo('metainfo.ini', verbose=True)
#for key,value in list(metadata.items()):
#    exec("%s = '%s'" % (key, value))
readme = open('README.md').read()
name = 'OpenAlea.Visualea'
description = 'OpenAlea Visual Programming Environment.'
long_description = readme
authors = 'OpenAlea consortium'
authors_email = 'christophe pradal at cirad fr'
url = 'https://github.com/openalea/visualea'
license = 'Cecill'


namespace = 'openalea'
packages = find_namespace_packages(where='src', include=['openalea.*'])
package_dir = {'': 'src'}

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords='visual programming, openalea, Scientific Workflows',

    # Packages

    packages = packages,
    package_dir = package_dir,
    package_data = {'openalea.visualea.resources' : ['*.ui', '*.png'],},
    include_package_data = True,
    zip_safe = False,

    # Scripts
    entry_points = { 'gui_scripts': [
                           'visualea = openalea.visualea.visualea_script:start_gui',
                           'aleashell = openalea.visualea.shell:main',],
                    },

    #postinstall_scripts = ['visualea_postinstall'],
    share_dirs = { 'share' : 'share' },

    # Dependencies
    setup_requires = ['openalea.deploy'],
    )


