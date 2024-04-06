#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree
import re

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'optima-ml'
DESCRIPTION = 'Distributed hyperparameter optimization and input variable selection for artificial neural networks.'
URL = 'https://gitlab.cern.ch/atlas-germany-dresden-vbs-group/optima'
EMAIL = 'erik.bachmann@tu-dresden.de'
AUTHOR = 'E. Bachmann'
REQUIRES_PYTHON = '>=3.9.0'  # TODO: find minimum!
VERSION = re.search('^__version__\s*=\s*"(.*)"', open('OPTIMA/optima.py').read(), re.M).group(1)

# Which platforms are supported?
PLATFORMS = ['linux', 'darwin']

REQUIRED = [
    'optuna==3.5.0',
    'ray[data,train,tune]==2.9.2',
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'seaborn',
    'tabulate',
    'scikit-learn',
] + (['multiprocess'] if sys.platform == 'darwin' else [])


EXTRAS = {
    'keras': ['tensorflow==2.15.0'] if sys.platform == 'linux' else ['tensorflow-macos==2.15.0'],
    'lightning': ['torch==2.1.2', 'lightning==2.1.2'],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    platforms=PLATFORMS,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points={
        'console_scripts': [
            'optima = OPTIMA.optima:main',
            'manage_ray_nodes = OPTIMA.helpers.manage_ray_nodes:main',
        ],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GPL',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 3 - Alpha'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
